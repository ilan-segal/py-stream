from typing import (
    Callable,
    Generic,
    Iterable,
    TypeVar,
)


T = TypeVar('T')
R = TypeVar('R')


class _Transformation(Generic[T, R]):
    """
    Abstract Stream transformation.
    """

    _func: Callable[[T], R]

    def __init__(self, func: Callable[[T], R]) -> None:
        self._func = func

    def apply(self, inputs: Iterable[T]) -> Iterable[R]:
        """
        Given an input iterable, return a transformed iterable according to func.
        """
        raise NotImplementedError


class _ElementWiseTransformation(_Transformation[T, R]):
    """
    Transforms each element of the iterable independently.
    """
    
    def apply(self, inputs: Iterable[T]) -> Iterable[R]:
        return map(self._func, inputs)


class _FlatTransformation(_Transformation[T, Iterable[R]]):
    """
    Flattens the resultant iterables of func into a single iterable before returning.
    """

    def apply(self, inputs: Iterable[T]) -> Iterable[R]:
        outputs = map(self._func, inputs)
        flattened_outputs = [item for output in outputs for item in output]
        return flattened_outputs


class _CollectiveTransformation(_Transformation[Iterable[T], Iterable[R]]):
    """
    Modifies the entire iterable altogether. Useful for reversing a list, for example.
    """

    def apply(self, inputs: Iterable[T]) -> Iterable[R]:
        return self._func(inputs)