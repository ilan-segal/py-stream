import unittest
from pythonstream import EagerStream


class TestEagerConcat(unittest.TestCase):

    def test_concat_same_type(self):
        s1 = EagerStream([1, 2, 3])
        s2 = EagerStream([4, 5, 6])
        s1_concat_s2 = s1.concat(s2)
        self.assertEqual(s1_concat_s2, EagerStream([1, 2, 3, 4, 5, 6]))

    def test_concat_different_type(self):
        s1 = EagerStream([1, 2, 3])
        s2 = EagerStream(['4', '5', '6'])
        s1_concat_s2 = s1.concat(s2)
        self.assertEqual(s1_concat_s2, EagerStream([1, 2, 3, '4', '5', '6']))

    def test_concat_empty_with_non_empty(self):
        empty = EagerStream([])
        non_empty = EagerStream([1, 2, 3])
        self.assertEqual(non_empty, non_empty.concat(empty))
        self.assertEqual(non_empty, empty.concat(non_empty))

    def test_concat_empty_with_empty(self):
        s1 = EagerStream([])
        s2 = EagerStream([])
        concat = s1.concat(s2)
        self.assertEqual(s1, s1.concat(s2))
        self.assertEqual(s1, s2.concat(s1))
        self.assertEqual(len(concat), 0)

    def test_add(self):
        s1 = EagerStream([1, 2, 3])
        s2 = EagerStream([4, 5, 6])
        s1_concat_s2 = s1 + s2
        self.assertEqual(s1_concat_s2, EagerStream([1, 2, 3, 4, 5, 6]))



class TestEagerFilter(unittest.TestCase):

    def test_filter(self):
        items = [1, 2, -1, -2, 15]
        s = (
            EagerStream(items)
            .filter(lambda n: n < 2)
        )
        self.assertEqual(s, EagerStream([1, -1, -2]))

    def test_filter_chain(self):
        items = [1, 2, 3, 4, 5, 6]
        s = (
            EagerStream(items)
            .filter(lambda n: n > 3)
            .filter(lambda n: n % 2 == 0)
        )
        self.assertEqual(s, EagerStream([4, 6]))

    def test_filter_always_true(self):
        items = [1, 2, 3, 4]
        s = (
            EagerStream(items)
            .filter(lambda _: True)
        )
        self.assertEqual(s, EagerStream(items))

    def test_filter_always_false(self):
        items = [1, 2, 3, 4]
        s = (
            EagerStream(items)
            .filter(lambda _: False)
        )
        self.assertEqual(s, EagerStream([]))


class TestEagerFlatMap(unittest.TestCase):

    def test_flat_map(self):
        items = [1, 2, 3]
        def multiply_element(n: int) -> list[int]:
            return [n] * n
        s = (
            EagerStream(items)
            .flat_map(multiply_element)
        )
        self.assertEqual(s, EagerStream([1, 2, 2, 3, 3, 3]))

    def test_flat_map_empty(self):
        items = [1, 2, 3]
        def empty_stream(n: int) -> list[int]:
            return []
        s = (
            EagerStream(items)
            .flat_map(empty_stream)
        )
        self.assertEqual(s, EagerStream([]))

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
            EagerStream(items)
            .flat_map(get_prime_factors)
        )
        self.assertEqual(s, EagerStream([2, 5, 11, 2, 3]))


class TestEagerMap(unittest.TestCase):

    def test_map_chain(self):
        s = (
            EagerStream([0, 1, 2])
            .map(lambda x: x*x)  # [0, 1, 4]
            .map(lambda x: chr(ord('a') + x))  # ['a', 'b', 'e']
            .map(lambda c: c*3)  # ['aaa', 'bbb', 'eee']
        )
        self.assertEqual(s, EagerStream(['aaa', 'bbb', 'eee']))


class TestEagerReverse(unittest.TestCase):

    def test_reverse(self):
        s = (
            EagerStream([0, 1, 2])
            .reverse()
        )
        self.assertEqual(s, EagerStream([2, 1, 0]))


class TestEagerSort(unittest.TestCase):

    def test_sort_no_key(self):
        items = [1, -1, 2, -2, 0]
        s = (
            EagerStream(items)
            .sorted()
        )
        self.assertEqual(s, EagerStream(sorted(items)))

    def test_sort_no_key_reverse(self):
        items = [1, -1, 2, -2, 0]
        s = (
            EagerStream(items)
            .sorted(reverse=True)
        )
        self.assertEqual(s, EagerStream(sorted(items, reverse=True)))

    def test_sort_with_key(self):
        items = ['three', 'two', 'one']
        key = {
            'one': 1,
            'two': 2,
            'three': 3,
        }
        s = (
            EagerStream(items)
            .sorted(key=key.get)
        )
        self.assertEqual(s, EagerStream(sorted(items, key=lambda x: key[x])))

    def test_sort_with_key_reverse(self):
        items = ['three', 'two', 'one']
        key = {
            'one': 1,
            'two': 2,
            'three': 3,
        }
        s = (
            EagerStream(items)
            .sorted(key=key.get, reverse=True)
        )
        self.assertEqual(s, EagerStream(sorted(items, key=lambda x: key[x], reverse=True)))

class TestEagerUnique(unittest.TestCase):

    def test_unique(self):
        items = [1, 1, 2, 1, 3, 2]
        s = EagerStream(items).unique()
        self.assertEqual(s, EagerStream(set(items)))

    def test_unique_empty(self):
        s = EagerStream([]).unique()
        self.assertEqual(s, EagerStream(set()))


class TestEagerAsList(unittest.TestCase):

    def test_as_list(self):
        items = [1, 1, 2, 1, 3, 2]
        s = EagerStream(items).as_list()
        self.assertEqual(s, items)


class TestEagerCount(unittest.TestCase):

    def test_count(self):
        items = [1, 1, 2, 1, 3, 2]
        s = EagerStream(items)
        self.assertEqual(s.count(), len(items))

    def test_len(self):
        items = [1, 1, 2, 1, 3, 2]
        s = EagerStream(items)
        self.assertEqual(len(s), len(items))


class TestEagerFindFirst(unittest.TestCase):

    def test_find_first(self):
        items = [-1, -2, -3, 5, 2, 0]
        first = EagerStream(items).find_first(lambda x: x >= 0)
        self.assertEqual(first, 5)


class TestEagerGetFirstOrLast(unittest.TestCase):

    def test_get_first(self):
        items = [-1, -2, -3, 5, 2, 0]
        first = EagerStream(items).get_first()
        self.assertEqual(first, -1)

    def test_get_first_none(self):
        items = []
        first = EagerStream(items).get_first()
        self.assertIsNone(first)

    def test_get_last(self):
        items = [-1, -2, -3, 5, 2, 0]
        last = EagerStream(items).get_last()
        self.assertEqual(last, 0)

    def test_get_last_none(self):
        items = []
        last = EagerStream(items).get_last()
        self.assertIsNone(last)



if __name__ == '__main__':
    unittest.main()