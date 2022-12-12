from __future__ import annotations
from copy import deepcopy
from functools import reduce
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    Optional,
    TypeVar,
)


T = TypeVar('T')
R = TypeVar('R')


class Stream(Generic[T]):

    def __init__(self) -> None:
        raise NotImplementedError('Stream is an abstract class and cannot be constructed directly.')

    def map(self, func: Callable[[T], R]) -> Stream[R]:
        """
        Return a Stream containing this Stream's contents after being transformed 
        element-wise by func.
        """
        raise NotImplementedError

    def flat_map(self, func: Callable[[T], Stream[R]]) -> Stream[R]:
        """
        Use func to transform this Stream's contents into a collection of Streams,
        then concatenate said streams into one Stream.
        """
        raise NotImplementedError

    def concat(self, other: Stream[R]) -> Stream[T | R]:
        """
        Return a Stream containing this Stream's contents as well as other's contents.
        """
        raise NotImplementedError

    def filter(self, predicate: Callable[[T], bool]) -> Stream[T]:
        """
        Return a copy of this Stream's contents excluding items which cause
        predicate to return False when given as input.
        """
        raise NotImplementedError

    def sorted(self, key: Optional[Callable[[T], Any]] = None, reverse: bool = False) -> Stream[T]:
        """
        Return a sorted stream with optional key and reverse arguments. See built-in
        sorted function for role of key and reverse.
        """
        raise NotImplementedError

    def reduce(self, func: Callable[[R, T], R], initial: R) -> R:
        """
        Reduce the contents of this Stream to a single value using a reducing
        function and an initial value.
        """
        raise NotImplementedError

    def reverse(self) -> Stream[T]:
        """
        Return a Stream with this Stream's content in reverse order.
        """
        raise NotImplementedError

    def find_first(self, predicate: Callable[[T], bool]) -> Optional[T]:
        """
        Return the first element of this Stream for which predicate returns True.
        """
        raise NotImplementedError

    def get_first(self) -> Optional[T]:
        """
        Return the first element of this Stream.
        """
        raise NotImplementedError

    def get_last(self) -> Optional[T]:
        """
        Return the last element of this Stream.
        """
        raise NotImplementedError

    def as_list(self) -> list[T]:
        """
        Return a deep copy of this Stream's contents as a list.
        """
        raise NotImplementedError

    def count(self) -> int:
        """
        Return the number of elements in this Stream.
        """
        return len(self)

    def __add__(self, other: Stream[R]) -> Stream[T | R]:
        raise NotImplementedError

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Stream):
            return False
        return self.as_list() == __o.as_list()

    def __len__(self) -> int:
        return len(self.as_list())


class EagerStream(Stream[T]):

    __contents: list[T]

    def __init__(self, contents: Iterable[T]) -> None:
        self.__contents = deepcopy([c for c in contents])

    def map(self, func: Callable[[T], R]) -> EagerStream[R]:
        return EagerStream(map(func, self.__contents))

    def flat_map(self, func: Callable[[T], Stream[R]]) -> EagerStream[R]:
        streams = map(func, self.__contents)
        flattened_contents = [c for stream in streams for c in stream.as_list()]
        return EagerStream(flattened_contents)

    def concat(self, other: Stream[R]) -> EagerStream[T | R]:
        return self + other

    def filter(self, predicate: Callable[[T], bool]) -> EagerStream[T]:
        return EagerStream(filter(predicate, self.__contents))

    def sorted(self, key: Optional[Callable[[T], Any]] = None, reverse: bool = False) -> EagerStream[T]:
        if key is None:
            return EagerStream(sorted(self.__contents, reverse=reverse))  # type: ignore
        return EagerStream(sorted(self.__contents, key=key, reverse=reverse))

    def reduce(self, func: Callable[[R, T], R], initial: R) -> R:
        return reduce(func, self.__contents, initial)

    def reverse(self) -> EagerStream[T]:
        return EagerStream(self.__contents[::-1])

    def find_first(self, predicate: Callable[[T], bool]) -> Optional[T]:
        for item in self.__contents:
            if predicate(item):
                return item
        return None

    def get_first(self) -> Optional[T]:
        if len(self.__contents) == 0:
            return None 
        return self.__contents[0]

    def get_last(self) -> Optional[T]:
        if len(self.__contents) == 0:
            return None 
        return self.__contents[-1]

    def as_list(self) -> list[T]:
        return deepcopy(self.__contents)

    def __add__(self, other: Stream[R]) -> EagerStream[T | R]:
        assert isinstance(other, Stream), \
            f'Stream concatenation not supported between types {type(self)}, {type(other)}'
        return EagerStream(self.as_list() + other.as_list())


NEXT_R = TypeVar('NEXT_R')


class _Transformation(Generic[R]):
    """
    Operation on an iterable. Exact behaviour is defined by func.
    """

    __result_getter: Callable[[], Iterable[R]]

    def __init__(self, func: Callable[[], Iterable[R]]) -> None:
        self.__result_getter = func

    def then(self, next_func: Callable[[Iterable[R]], Iterable[NEXT_R]]) -> _Transformation[NEXT_R]:
        def next_func_wrapper() -> Iterable[NEXT_R]:
            intermediate = self.get()
            return next_func(intermediate)
        return _Transformation(next_func_wrapper)

    def get(self) -> Iterable[R]:
        """
        Given an input iterable, return a transformed iterable according to func.
        """
        return self.__result_getter()


class LazyStream(Stream[T]):

    __transformation: _Transformation[T]

    @staticmethod
    def of(contents: Iterable[T]) -> LazyStream[T]:
        def identity() -> Iterable[T]:
            return deepcopy(contents)
        identity_transformation = _Transformation(identity)
        return LazyStream(identity_transformation)

    def __init__(
        self,
        transformation: _Transformation[T],
        ) -> None:
        """
        This constructor should NOT be used by the client. To create a LazyStream
        instance, see `LazyStream.of`
        """
        self.__transformation = transformation

    def __chain_transformation(
        self, 
        transform_function: Callable[[Iterable[T]], Iterable[R]],
        ) -> LazyStream[R]:
        """
        Helper function for chaining transformations together.
        """
        return LazyStream(self.__transformation.then(transform_function))

    #############################
    ## INTERMEDIATE OPERATIONS ##
    #############################

    def map(self, func: Callable[[T], R]) -> LazyStream[R]:
        def elementwise_func(inputs: Iterable[T]) -> Iterable[R]:
            return map(func, inputs)
        return self.__chain_transformation(elementwise_func)
        
    def flat_map(self, func: Callable[[T], Stream[R]]) -> LazyStream[R]:
        def flatten_func(inputs: Iterable[T]) -> Iterable[R]:
            output_streams = map(func, inputs)
            flattened_contents = [item for stream in output_streams for item in stream.as_list()]
            return flattened_contents
        return self.__chain_transformation(flatten_func)

    def concat(self, other: Stream[R]) -> LazyStream[T | R]:
        def concat_func(inputs: Iterable[T]) -> Iterable[T | R]:
            return [item for item in inputs] + other.as_list()
        return self.__chain_transformation(concat_func)

    def filter(self, predicate: Callable[[T], bool]) -> LazyStream[T]:
        def filter_func(inputs: Iterable[T]) -> Iterable[T]:
            return filter(predicate, inputs)
        return self.__chain_transformation(filter_func)

    def sorted(self, key: Optional[Callable[[T], Any]] = None, reverse: bool = False) -> LazyStream[T]:
        def sorted_func(inputs: Iterable[T]) -> Iterable[T]:
            if key is None:
                return sorted(inputs, reverse=reverse)  # type: ignore
            return sorted(inputs, key=key, reverse=reverse)
        return self.__chain_transformation(sorted_func)

    def reverse(self) -> LazyStream[T]:
        def reverse_func(inputs: Iterable[T]) -> Iterable[T]:
            return [item for item in inputs][::-1]
        return self.__chain_transformation(reverse_func)
        

    #########################
    ## TERMINAL OPERATIONS ##
    #########################

    def __get_evaluated_contents(self) -> Iterable[T]:
        return self.__transformation.get()
    
    def as_list(self) -> list[T]:
        return [item for item in self.__get_evaluated_contents()]

    def reduce(self, func: Callable[[R, T], R], initial: R) -> R:
        evaluated = self.__get_evaluated_contents()
        return reduce(func, evaluated, initial)

    def find_first(self, predicate: Callable[[T], bool]) -> Optional[T]:
        evaluated = self.__get_evaluated_contents()
        for item in evaluated:
            if predicate(item):
                return item
        return None

    def get_first(self) -> Optional[T]:
        evaluated = self.as_list()
        if len(evaluated) == 0:
            return None
        return evaluated[0]

    def get_last(self) -> Optional[T]:
        evaluated = self.as_list()
        if len(evaluated) == 0:
            return None
        return evaluated[-1]


    ########################
    ## BUILT-IN OVERRIDES ##
    ########################

    def __add__(self, other: Stream[R]) -> Stream[R | T]:
        assert isinstance(other, Stream), \
            f'Stream concatenation not supported between types {type(self)}, {type(other)}'
        return self.concat(other)
