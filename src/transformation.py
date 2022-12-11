from __future__ import annotations
from typing import (
    Callable,
    Generic,
    Iterable,
    TypeVar,
)


R = TypeVar('R')
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
