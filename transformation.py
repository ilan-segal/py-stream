from __future__ import annotations
from typing import (
    Callable,
    Generic,
    Iterable,
    TypeVar,
)


T = TypeVar('T')
R = TypeVar('R')
NEXT_R = TypeVar('NEXT_R')


class _Transformation(Generic[T, R]):
    """
    Operation on an iterable. Exact behaviour is defined by func.
    """

    __func: Callable[[Iterable[T]], Iterable[R]]

    def __init__(self, func: Callable[[Iterable[T]], Iterable[R]]) -> None:
        self.__func = func

    def then(self, next_transformation: _Transformation[R, NEXT_R]) -> _Transformation[T, NEXT_R]:
        def next_func(inputs: Iterable[T]) -> Iterable[NEXT_R]:
            intermediate = self.apply(inputs)
            return next_transformation.apply(intermediate)
        return _Transformation(next_func)

    def apply(self, inputs: Iterable[T]) -> Iterable[R]:
        """
        Given an input iterable, return a transformed iterable according to func.
        """
        return self.__func(inputs)
