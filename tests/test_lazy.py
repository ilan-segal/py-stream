import unittest
from pythonstream import LazyStream


class TestLazyConcat(unittest.TestCase):

    def test_concat_same_type(self):
        s1 = LazyStream([1, 2, 3])
        s2 = LazyStream([4, 5, 6])
        s1_concat_s2 = s1.concat(s2)
        self.assertEqual(s1_concat_s2, LazyStream([1, 2, 3, 4, 5, 6]))

    def test_concat_different_type(self):
        s1 = LazyStream([1, 2, 3])
        s2 = LazyStream(['4', '5', '6'])
        s1_concat_s2 = s1.concat(s2)
        self.assertEqual(s1_concat_s2, LazyStream([1, 2, 3, '4', '5', '6']))

    def test_concat_empty_with_non_empty(self):
        empty = LazyStream([])
        non_empty = LazyStream([1, 2, 3])
        self.assertEqual(non_empty, non_empty.concat(empty))
        self.assertEqual(non_empty, empty.concat(non_empty))

    def test_concat_empty_with_empty(self):
        s1 = LazyStream([])
        s2 = LazyStream([])
        concat = s1.concat(s2)
        self.assertEqual(s1, s1.concat(s2))
        self.assertEqual(s1, s2.concat(s1))
        self.assertEqual(len(concat), 0)

    def test_add(self):
        s1 = LazyStream([1, 2, 3])
        s2 = LazyStream([4, 5, 6])
        s1_concat_s2 = s1 + s2
        self.assertEqual(s1_concat_s2, LazyStream([1, 2, 3, 4, 5, 6]))



class TestLazyFilter(unittest.TestCase):

    def test_filter(self):
        items = [1, 2, -1, -2, 15]
        s = (
            LazyStream(items)
            .filter(lambda n: n < 2)
        )
        self.assertEqual(s, LazyStream([1, -1, -2]))

    def test_filter_chain(self):
        items = [1, 2, 3, 4, 5, 6]
        s = (
            LazyStream(items)
            .filter(lambda n: n > 3)
            .filter(lambda n: n % 2 == 0)
        )
        self.assertEqual(s, LazyStream([4, 6]))

    def test_filter_always_true(self):
        items = [1, 2, 3, 4]
        s = (
            LazyStream(items)
            .filter(lambda _: True)
        )
        self.assertEqual(s, LazyStream(items))

    def test_filter_always_false(self):
        items = [1, 2, 3, 4]
        s = (
            LazyStream(items)
            .filter(lambda _: False)
        )
        self.assertEqual(s, LazyStream([]))


class TestLazyFlatMap(unittest.TestCase):

    def test_flat_map(self):
        items = [1, 2, 3]
        def multiply_element(n: int) -> list[int]:
            return [n] * n
        s = (
            LazyStream(items)
            .flat_map(multiply_element)
        )
        self.assertEqual(s, LazyStream([1, 2, 2, 3, 3, 3]))

    def test_flat_map_empty(self):
        items = [1, 2, 3]
        def empty_stream(n: int) -> list[int]:
            return []
        s = (
            LazyStream(items)
            .flat_map(empty_stream)
        )
        self.assertEqual(s, LazyStream([]))

    def test_flat_map_prime_factors(self):
        items = [10, 11, 12]
        def is_prime(n: int) -> bool:
            for factor in range(2, n):
                if n % factor == 0:
                    return False
            return True
        def get_factors(n: int) -> filter:
            potential_factors = range(2, n+1)
            return filter(lambda f: n % f == 0, potential_factors)
        def get_prime_factors(n: int) -> filter:
            factors = get_factors(n)
            return filter(is_prime, factors)
        s = (
            LazyStream(items)
            .flat_map(get_prime_factors)
        )
        self.assertEqual(s, LazyStream([2, 5, 11, 2, 3]))


class TestLazyMap(unittest.TestCase):

    def test_map_chain(self):
        s = (
            LazyStream([0, 1, 2])
            .map(lambda x: x*x)  # [0, 1, 4]
            .map(lambda x: chr(ord('a') + x))  # ['a', 'b', 'e']
            .map(lambda c: c*3)  # ['aaa', 'bbb', 'eee']
        )
        self.assertEqual(s, LazyStream(['aaa', 'bbb', 'eee']))


class TestLazyReverse(unittest.TestCase):

    def test_reverse(self):
        s = (
            LazyStream([0, 1, 2])
            .reverse()
        )
        self.assertEqual(s, LazyStream([2, 1, 0]))


class TestLazySort(unittest.TestCase):

    def test_sort_no_key(self):
        items = [1, -1, 2, -2, 0]
        s = (
            LazyStream(items)
            .sorted()
        )
        self.assertEqual(s, LazyStream(sorted(items)))

    def test_sort_no_key_reverse(self):
        items = [1, -1, 2, -2, 0]
        s = (
            LazyStream(items)
            .sorted(reverse=True)
        )
        self.assertEqual(s, LazyStream(sorted(items, reverse=True)))

    def test_sort_with_key(self):
        items = ['three', 'two', 'one']
        key = {
            'one': 1,
            'two': 2,
            'three': 3,
        }
        s = (
            LazyStream(items)
            .sorted(key=key.get)
        )
        self.assertEqual(s, LazyStream(sorted(items, key=lambda x: key[x])))

    def test_sort_with_key_reverse(self):
        items = ['three', 'two', 'one']
        key = {
            'one': 1,
            'two': 2,
            'three': 3,
        }
        s = (
            LazyStream(items)
            .sorted(key=key.get, reverse=True)
        )
        self.assertEqual(s, LazyStream(sorted(items, key=lambda x: key[x], reverse=True)))

class TestLazyUnique(unittest.TestCase):

    def test_unique(self):
        items = [1, 1, 2, 1, 3, 2]
        s = LazyStream(items).unique()
        self.assertEqual(s, LazyStream(set(items)))

    def test_unique_empty(self):
        s = LazyStream([]).unique()
        self.assertEqual(s, LazyStream(set()))


class TestLazyAsList(unittest.TestCase):

    def test_as_list(self):
        items = [1, 1, 2, 1, 3, 2]
        s = LazyStream(items).as_list()
        self.assertEqual(s, items)


class TestLazyCount(unittest.TestCase):

    def test_count(self):
        items = [1, 1, 2, 1, 3, 2]
        s = LazyStream(items)
        self.assertEqual(s.count(), len(items))

    def test_len(self):
        items = [1, 1, 2, 1, 3, 2]
        s = LazyStream(items)
        self.assertEqual(len(s), len(items))


class TestLazyFindFirst(unittest.TestCase):

    def test_find_first(self):
        items = [-1, -2, -3, 5, 2, 0]
        first = LazyStream(items).find_first(lambda x: x >= 0)
        self.assertEqual(first, 5)


class TestLazyGetFirstOrLast(unittest.TestCase):

    def test_get_first(self):
        items = [-1, -2, -3, 5, 2, 0]
        first = LazyStream(items).get_first()
        self.assertEqual(first, -1)

    def test_get_first_none(self):
        items = []
        first = LazyStream(items).get_first()
        self.assertIsNone(first)

    def test_get_last(self):
        items = [-1, -2, -3, 5, 2, 0]
        last = LazyStream(items).get_last()
        self.assertEqual(last, 0)

    def test_get_last_none(self):
        items = []
        last = LazyStream(items).get_last()
        self.assertIsNone(last)



if __name__ == '__main__':
    unittest.main()