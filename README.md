# Streams for Python

Prototypical implementation of the Stream data structure, taking heavy inspiration from Java 8+ streams. This data structure is for chaining methods on ordered collections of typed data.

## Roadmap

I intend to test & publish this module to Pip with every commit to `main`. This will be implemented using GitHub's automated CI/CD tools.

## Generic Type

A Stream has a single type parameter which indicates the type of data contained in the Stream after transformations have been applied. Your IDE's type checker should be able to infer a Stream's type, even after several chained operations.

## Eager vs. Lazy

There exist two implementations of the abstract `Stream` base class:

* `EagerStream`
* `LazyStream`

As their names suggest, `EagerStream` evaluates transformations as soon as possible while `LazyStream` delays all transformations until a terminal operation is invoked.

## Chained operations

A Stream has several transformational methods that return new Streams. When chaining these methods together, each new Stream is based on a deep copy of the previous Stream's contents. A Stream is never modified in-place.

### `Stream.concat`

This method combines the contents of this stream with another Stream:

```python
s = (
    EagerStream([1, 2, 3])
    .concat(EagerStream([4, 5, 6]))
)  # EagerStream([1, 2, 3, 4, 5, 6])
```

### `Stream.filter`

You may filter a Stream's contents based on some predicate:

```python
s = (
    EagerStream([1, 2, 3, 4])
    .filter(lambda x: x % 2 == 0)  # EagerStream([2, 4])
    .filter(lambda x: x < 4)  # EagerStream([2])
)
```

### `Stream.flat_map`

Streams support monadic-like behaviour with the `flat_map` method, which accepts functions that return other Streams. The accepted function is applied to each element of the Stream then the resultant Streams are all concatenated into the returned Stream. Example below:

```python
def get_prime_factors(n: int) -> Stream[int]:
    # Return Stream containing the prime factorization of n

get_prime_factors(10)  # EagerStream([2, 5])
get_prime_factors(11)  # EagerStream([11])
get_prime_factors(12)  # EagerStream([2, 2, 3])

s = (
    EagerStream([10, 11, 12])
    .flat_map(get_prime_factors)
)  # EagerStream([2, 5, 11, 2, 2, 3])

```

### `Stream.map`

Using the `map` method you can transform a Stream element-wise:

```python
a = [0, 1, 2]
b = (
    EagerStream(a)
    .map(lambda x: x*x)  # [0, 1, 4]
    .map(lambda x: chr(ord('a') + x))  # ['a', 'b', 'e']
    .map(lambda c: c*3)  # ['aaa', 'bbb', 'eee']
)
```

### `Stream.reverse`

You may reverse the contents of a Stream:

```python
s = (
    EagerStream([1, 2, 3])
    .reverse()  # EagerStream([3, 2, 1])
)
```

### `Stream.sorted`

You may create a sorted Stream:

```python
s = (
    EagerStream([1, -1, 5, 0])
    .sorted()  # EagerStream([-1, 0, 1, 5])
)
```

Optional `key` and `reverse` arguments may be provided to the method as with Python's built-in `sorted` function.

### `Stream.unique`

You may take all unique elements of a Stream (preserving order of contents):

```python
s = (
    EagerStream([1, 1, 2, 1, 3, 2])
    .unique()  # EagerStream([1, 2, 3])
)
```

Optional `key` and `reverse` arguments may be provided to the method as with Python's built-in `sorted` function.

## Terminal Operations

A Stream has several methods which return a non-Stream object. These are called *terminal operations* because they come at the end of a Stream's "life cycle."

### `Stream.as_list`

This method takes no arguments and returns the Stream's deep-copied contents in a `list`.

### `Stream.count`

Return the number of elements in the Stream.

### `Stream.find_first`

Given some predicate, return the first element of the Stream which matches said predicate. If none match, return None.

### `Stream.get_first`

Return the first element of the Stream.

### `Stream.get_last`

Return the last element of the Stream.

## Built-in overrides

### `__add__`

Equivalent to `Stream.concat()`.

### `__iter__`

Return an iterable version of the Stream.

### `__len__`

Equivalent to `Stream.count()`