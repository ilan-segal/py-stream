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

    __contents: list[T]

    def __init__(self, contents: Iterable[T]) -> None:
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
        return Stream(filter(predicate, self.__contents))

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
        return Stream(map(func, self.__contents))

    def flat_map(self, func: Callable[[T], Stream[R]]) -> Stream[R]:
        streams = map(func, self.__contents)
        flattened_contents = [c for stream in streams for c in stream.as_list()]
        return Stream(flattened_contents)

    def concat(self, other: Stream[R]) -> Stream[T | R]:
        return self + other

    def filter(self, predicate: Callable[[T], bool]) -> Stream[T]:
        return Stream(filter(predicate, self.__contents))

    def sorted(self, key: Optional[Callable[[T], Any]] = None, reverse: bool = False) -> Stream[T]:
        if key is None:
            return Stream(sorted(self.__contents, reverse=reverse))  # type: ignore
        return Stream(sorted(self.__contents, key=key, reverse=reverse))

    def reduce(self, func: Callable[[R, T], R], initial: R) -> R:
        return reduce(func, self.__contents, initial)

    def reverse(self) -> Stream[T]:
        return Stream(self.__contents[::-1])

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
        return Stream(self.__contents + other.__contents)