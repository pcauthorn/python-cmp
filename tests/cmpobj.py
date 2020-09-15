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
        self.assertFalse(r.match)
        self.assertEqual(len(r.items), 1)

    def test_list(self):
        l1 = [1, 2, 3, 4]
        l2 = [1, 2, 4, 5]
        r = self.cmp.compare(l1, l2)
        self.assertFalse(r.match)
        self.assertEqual(len(r.items), 2)
        self.assertEqual(r.items[0].path, [2])
        self.assertEqual(r.items[1].path, [3])

    def test_mix(self):
        o1 = dict(a={1, 2, 3}, b=dict(c=('a', 'b'), d={42: 43, 'd': 1.1}))
        o2 = dict(a={1, 2}, b=dict(c=('a',), d={42: 43, 'd': 1.1}))
        r = self.cmp.compare(o1, o2)
        self.assertFalse(r.match)
        paths = []
        for i, v in r.items.items():
            if not v.items:
                continue
            for j in v.items:
                paths.append(j.path)
        self.assertEqual(paths, [['a', 'b', 'b'], ['a', 2]])

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
            self.assertTrue(r.match)
            if r.items:
                self.assertEqual(len(r.items), 2)
        self.assertIsNone(self.cmp.compare(d1, d1))

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
