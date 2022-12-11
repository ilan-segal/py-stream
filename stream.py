from __future__ import annotations
from copy import deepcopy
from functools import reduce
from transformation import (
    _Transformation,
)
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
        raise NotImplementedError

    def __iter__(self) -> Iterable[T]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __add__(self, other: Stream[R]) -> Stream[T | R]:
        raise NotImplementedError


class EagerStream(Stream[T]):

    __contents: list[T]

    def __init__(self, contents: Iterable[T]) -> None:
        self.__contents = deepcopy([c for c in contents])

    def map(self, func: Callable[[T], R]) -> Stream[R]:
        return EagerStream(map(func, self.__contents))

    def flat_map(self, func: Callable[[T], Stream[R]]) -> Stream[R]:
        streams = map(func, self.__contents)
        flattened_contents = [c for stream in streams for c in stream.as_list()]
        return EagerStream(flattened_contents)

    def concat(self, other: Stream[R]) -> Stream[T | R]:
        return self + other

    def filter(self, predicate: Callable[[T], bool]) -> Stream[T]:
        return EagerStream(filter(predicate, self.__contents))

    def sorted(self, key: Optional[Callable[[T], Any]] = None, reverse: bool = False) -> Stream[T]:
        if key is None:
            return EagerStream(sorted(self.__contents, reverse=reverse))  # type: ignore
        return EagerStream(sorted(self.__contents, key=key, reverse=reverse))

    def reduce(self, func: Callable[[R, T], R], initial: R) -> R:
        return reduce(func, self.__contents, initial)

    def reverse(self) -> Stream[T]:
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

    def count(self) -> int:
        return len(self.__contents)

    def __iter__(self) -> Iterable[T]:
        return self.as_list()

    def __len__(self) -> int:
        return self.count()

    def __add__(self, other: Stream[R]) -> Stream[T | R]:
        assert isinstance(other, Stream), \
            f'Stream concatenation not supported between types {type(self)}, {type(other)}'
        return EagerStream(self.as_list() + other.as_list())


InitType = TypeVar('InitType')
NextType = TypeVar('NextType')

class LazyStream(Generic[T, R], Stream[R]):
    """
    T = Initial contents type
    R = "Return" type
    """

    __initial_contents: list[T]
    __transformation: _Transformation[T, R]

    @staticmethod
    def of(contents: Iterable[InitType]) -> LazyStream[InitType, InitType]:
        def identity(x: Iterable[InitType]) -> Iterable[InitType]:
            return x
        identity_transformation = _Transformation(identity)
        return LazyStream(contents, identity_transformation)

    def __init__(
        self,
        contents: Iterable[T],
        transformation: _Transformation[T, R],
        ) -> None:
        """
        This constructor should NOT be used by the client. To create a LazyStream
        instance, see `LazyStream.of`
        """
        self.__initial_contents = deepcopy([c for c in contents])
        self.__transformation = transformation

    def __chain_transformation(
        self, 
        transform_function: Callable[[Iterable[R]], Iterable[NextType]],
        ) -> LazyStream[T, NextType]:
        """
        Helper function for chaining transformations together.
        """
        return LazyStream(
            self.__initial_contents, 
            self.__transformation.then(_Transformation(transform_function))
        )

    #############################
    ## INTERMEDIATE OPERATIONS ##
    #############################

    def map(self, func: Callable[[R], NextType]) -> LazyStream[T, NextType]:
        def elementwise_func(inputs: Iterable[R]) -> Iterable[NextType]:
            return map(func, inputs)
        return self.__chain_transformation(elementwise_func)
        
    def flat_map(self, func: Callable[[R], Stream[NextType]]) -> LazyStream[T, NextType]:
        def flatten_func(inputs: Iterable[R]) -> Iterable[NextType]:
            output_streams = map(func, inputs)
            flattened_contents = [item for stream in output_streams for item in stream.as_list()]
            return flattened_contents
        return self.__chain_transformation(flatten_func)

    def concat(self, other: Stream[NextType]) -> LazyStream[T, R | NextType]:
        def concat_func(inputs: Iterable[R]) -> Iterable[R | NextType]:
            return [item for item in inputs] + other.as_list()
        return self.__chain_transformation(concat_func)

    def filter(self, predicate: Callable[[R], bool]) -> LazyStream[T, R]:
        def filter_func(inputs: Iterable[R]) -> Iterable[R]:
            return filter(predicate, inputs)
        return self.__chain_transformation(filter_func)

    def sorted(self, key: Optional[Callable[[R], Any]] = None, reverse: bool = False) -> LazyStream[T, R]:
        def sorted_func(inputs: Iterable[R]) -> Iterable[R]:
            if key is None:
                return sorted(inputs, reverse=reverse)  # type: ignore
            return sorted(inputs, key=key, reverse=reverse)
        return self.__chain_transformation(sorted_func)

    def reverse(self) -> LazyStream[T, R]:
        def reverse_func(inputs: Iterable[R]) -> Iterable[R]:
            return [item for item in inputs][::-1]
        return self.__chain_transformation(reverse_func)
        

    #########################
    ## TERMINAL OPERATIONS ##
    #########################

    def __get_evaluated_contents(self) -> Iterable[R]:
        return self.__transformation.apply(self.__initial_contents)
    
    def as_list(self) -> list[R]:
        return [item for item in self.__get_evaluated_contents()]

    def reduce(self, func: Callable[[NextType, R], NextType], initial: NextType) -> NextType:
        evaluated = self.__get_evaluated_contents()
        return reduce(func, evaluated, initial)

    def find_first(self, predicate: Callable[[R], bool]) -> Optional[R]:
        evaluated = self.__get_evaluated_contents()
        for item in evaluated:
            if predicate(item):
                return item
        return None

    def get_first(self) -> Optional[R]:
        evaluated = self.as_list()
        if len(evaluated) == 0:
            return None
        return evaluated[0]

    def get_last(self) -> Optional[R]:
        evaluated = self.as_list()
        if len(evaluated) == 0:
            return None
        return evaluated[-1]

    def count(self) -> int:
        return len(self.as_list())


    ########################
    ## BUILT-IN OVERRIDES ##
    ########################

    def __iter__(self) -> Iterable[R]:
        return self.__get_evaluated_contents()

    def __len__(self) -> int:
        return self.count()

    def __add__(self, other: Stream[NextType]) -> Stream[NextType | R]:
        assert isinstance(other, Stream), \
            f'Stream concatenation not supported between types {type(self)}, {type(other)}'
        return self.concat(other)
