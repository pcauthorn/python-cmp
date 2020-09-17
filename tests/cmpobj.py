import unittest
from copy import deepcopy

from cmp.src import Cmp


class TestCmp(unittest.TestCase):
    def setUp(self):
        self.cmp = Cmp()

    def test_dict(self):
        d1 = dict(a=1, b=dict(c=3, d=42))
        d2 = deepcopy(d1)
        d2['b']['d'] = 43
        r = self.cmp.get_diffs(d1, d2)
        self.assertEqual(len(r), 3)
        self.assertTrue(all([not x.match for x in r]))

    def test_list(self):
        l1 = [1, 2, 3, 4]
        l2 = [1, 2, 4, 5]
        r = self.cmp.get_diffs(l1, l2)
        self.assertEqual(len(r), 3)
        self.assertFalse(all([x.match for x in r]))
        paths = [x.path for x in r if x]
        self.assertEqual(paths, [[], [2], [3]])

    def test_mix(self):
        o1 = dict(a={1, 2, 3}, b=dict(c=('a', 'b'), d={42: 43, 'd': 1.1}))
        o2 = dict(a={1, 2}, b=dict(c=('a',), d={42: 43, 'd': 1.1}))
        r = self.cmp.get_diffs(o1, o2)
        self.assertFalse(all([x.match for x in r]))

    def test_path(self):
        o1 = dict(a={1, 2, 3}, b=dict(c=('a', 'b'), d={42: 43, 'd': 1.1, 'e': [1, 2]}))
        o2 = dict(a={1, 2}, b=dict(c=('a',), d={42: 43, 'd': 1.1, 'e': [1, 3]}))
        r = self.cmp.get_diffs(o1, o2)
        paths = [x.path for x in r if x]
        self.assertEqual(paths, [[], ['a'], ['b'], ['b', 'c'], ['b', 'd'], ['b', 'd', 'e'], ['b', 'd', 'e', 1]])


class TestCmpArgs(unittest.TestCase):
    def setUp(self):
        self.cmp = Cmp()

    def test_order_lists(self):
        o1 = [1, 2, 3]
        o2 = [3, 2, 1]
        c1 = self.cmp.get_diffs(o1, o2, order_lists=False)
        self.assertNotEqual(len(c1), 0)
        c2 = self.cmp.get_diffs(o1, o2, order_lists=True)
        self.assertEqual(len(c2), 0)

    def test_include_matches(self):
        d1 = dict(a=1, b=dict(c=3, d=42))
        for r in [self.cmp.get_diffs(d1, d1, include_matches=True),
                  self.cmp.get_diffs(d1, deepcopy(d1), include_matches=True)]:
            self.assertGreater(len(r), 0)
            self.assertTrue(all([v.match for v in r]))
        self.assertEqual(self.cmp.get_diffs(d1, d1), [])

    def test_max_iteration(self):
        d1 = ['data'] * 10
        d2 = ['data'] * 3 + ['no_match_data'] * 7
        r = self.cmp.get_diffs(d1, d2, max_iteration=3)
        self.assertEqual(len(r), 0)
        r = self.cmp.get_diffs(d1, d2, max_iteration=4)
        self.assertEqual(len(r), 2)


class TestCmpFormatters(unittest.TestCase):
    def test_x(self):
        pass


class TestCmpComparators(unittest.TestCase):
    def test_x(self):
        pass


if __name__ == '__main__':
    unittest.main()
