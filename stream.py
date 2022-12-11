from __future__ import annotations
from copy import deepcopy
from functools import reduce
from typing import (
    Callable,
    Generic,
    Iterable,
    TypeVar,
)


T = TypeVar('T')
R = TypeVar('R')


class Stream(Generic[T]):
    """
    Iterable stream class with monad-like behaviours.
    """

    __contents: list[T]

    def __init__(self, contents: Iterable[T]) -> None:
        self.__contents = deepcopy([c for c in contents])

    def map(self, func: Callable[[T], R]) -> Stream[R]:
        """
        Return a Stream containing this Stream's contents after being transformed 
        element-wise by func.
        """
        return Stream(map(func, self.__contents))

    def flatMap(self, func: Callable[[T], Stream[R]]) -> Stream[R]:
        """
        Use func to transform this Stream's contents into a collection of Streams,
        then concatenate said streams into one Stream.
        """
        streams = map(func, self.__contents)
        flattened_contents = [c for stream in streams for c in stream]
        return Stream(flattened_contents)

    def concat(self, other: Stream[R]) -> Stream[T | R]:
        """
        Return a Stream containing this Stream's contents as well as other's contents.
        """
        return self + other

    def filter(self, predicate: Callable[[T], bool]) -> Stream[T]:
        """
        Return a copy of this Stream's contents excluding items which cause
        predicate to return False when given as input.
        """
        return Stream(filter(predicate, self.__contents))

    def reduce(self, func: Callable[[T, R], R], initial: R) -> R:
        """
        Reduce the contents of this Stream to a single value using a reducing
        function and an initial value.
        """
        return reduce(func, self.__contents, initial)

    def getFirst(self) -> T:
        """
        Return the first element of this Stream.
        """
        return self.__contents[0]

    def getLast(self) -> T:
        """
        Return the last element of this Stream.
        """
        return self.__contents[-1]

    def asList(self) -> list[T]:
        """
        Return a deep copy of this Stream's contents as a list.
        """
        return deepcopy(self.__contents)

    def __iter__(self) -> Iterable[T]:
        self.asList()

    def __len__(self) -> int:
        return len(self.__contents)

    def __add__(self, other: Stream[R]) -> Stream[T | R]:
        assert isinstance(other, Stream), \
            f'Stream concatenation not supported between types {type(self)}, {type(other)}'
        return Stream(self.__contents + other.__contents)