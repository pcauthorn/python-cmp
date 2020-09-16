import unittest
from copy import deepcopy

from cmp.code import Cmp


class TestCmp(unittest.TestCase):
    def setUp(self):
        self.cmp = Cmp()

    def test_dict(self):
        d1 = dict(a=1, b=dict(c=3, d=42))
        d2 = deepcopy(d1)
        d2['b']['d'] = 43
        r = self.cmp.compare(d1, d2)
        self.assertEqual(len(r), 3)
        self.assertTrue(all([not x.match for x in r]))

    def test_list(self):
        l1 = [1, 2, 3, 4]
        l2 = [1, 2, 4, 5]
        r = self.cmp.compare(l1, l2)
        self.assertEqual(len(r), 3)
        self.assertFalse(all([x.match for x in r]))
        paths = [x.path for x in r if x]
        self.assertEqual(paths, [[], [2], [3]])

    def test_mix(self):
        o1 = dict(a={1, 2, 3}, b=dict(c=('a', 'b'), d={42: 43, 'd': 1.1}))
        o2 = dict(a={1, 2}, b=dict(c=('a',), d={42: 43, 'd': 1.1}))
        r = self.cmp.compare(o1, o2)
        self.assertFalse(all([x.match for x in r]))
        paths = [x.path for x in r if x]
        self.assertEqual(paths, [[], ['a'], ['b'], ['b', 'c']])

    def test_path(self):
        pass


class TestCmpArgs(unittest.TestCase):
    def setUp(self):
        self.cmp = Cmp()

    def test_order(self):
        pass

    def test_include_matches(self):
        d1 = dict(a=1, b=dict(c=3, d=42))
        for r in [self.cmp.compare(d1, d1, include_matches=True),
                  self.cmp.compare(d1, deepcopy(d1), include_matches=True)]:
            self.assertGreater(len(r), 0)
            self.assertTrue(all([v.match for v in r]))

        self.assertEqual(self.cmp.compare(d1, d1), [])

    def test_max_iter(self):
        pass


class TestCmpFormatters(unittest.TestCase):
    def test_x(self):
        pass


class TestCmpComparators(unittest.TestCase):
    def test_x(self):
        pass


if __name__ == '__main__':
    unittest.main()
