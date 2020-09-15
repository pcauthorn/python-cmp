"""
Thoughts:
Handle significant digits as comparator + an arg be an arg as that shortcut for adding that comparator
fast_fail?

CmpResult:
match boolean
result format
path -> list of index or keys
obj
context

"""
import logging
from itertools import islice
from operator import eq

logger = logging.getLogger(__name__)


class Mismatches:
    Type = 'Type mismatch'
    Size = 'Size mismatch'
    MissingKey = 'Missing key'


class CmpResult:
    def __init__(self, match, path, diff=None, items=None):
        self.match = match
        self.path = path
        self.diff = diff
        self.items = items


class Cmp:

    def __init__(self, comparators=None, formatters=None):
        """
        :param comparators:
        dict:
         type: comparator
        :param formatters:
        dict:
         type : function(one, two) -> diff (a string unless something fancier is called for)
         MismatchType:str ->  "

        """
        formatters = formatters or {}
        self.comparators = comparators or {}
        mk = '<No Existent Key>'
        default_formatters = {Mismatches.Type: lambda o, t: f'{Mismatches.Type}: {type(o)} != {type(t)}',
                              Mismatches.Size: lambda o, t: f'{Mismatches.Size}: {len(o)} != {len(t)}',
                              Mismatches.MissingKey:
                                  lambda k1, k2: f'{Mismatches.MissingKey}: {k1 or mk} != {k2 or mk}'}
        default_formatters.update(formatters)
        self.formatters = default_formatters

    def _fmt(self, fmt_type, one, two):
        return self.formatters[fmt_type](one, two)

    def compare(self, one, two, include_matches=False, order=True, max_length=30, max_iter=1000, path=None):
        path = path if path is not None else []
        if one is two:
            logger.info('Objects are the same.  Returning match')
            return CmpResult(True, path, diff='Same object compared') if include_matches else None
        if type(one) != type(two):
            return CmpResult(False, path, diff=self._fmt(Mismatches.Type, one, two))
        cmp = self.comparators.get(type(one))
        if cmp:
            return cmp.compare(one, two, order=order, max_length=max_length, path=path, include_matches=include_matches)
        if isinstance(one, dict):
            missing_in_one = two.keys() - one.keys()
            items = {}
            for k, v1 in one.items():
                if k not in two:
                    items[k] = CmpResult(False, path + [k], diff=self._fmt(Mismatches.MissingKey, k, None))
                else:
                    v2 = two.get(k)
                    r = self.compare(v1,
                                     v2,
                                     order=order,
                                     max_length=max_length,
                                     path=path + [k],
                                     include_matches=include_matches)
                    if r and not r.match or include_matches:
                        items[k] = r
            for k in missing_in_one:
                items[k] = CmpResult(False, path + [k], diff=self._fmt(Mismatches.MissingKey, None, k))
            match = all([v.match for k, v in items.items()])
            return CmpResult(match, path, items=items) if not match or include_matches else None
        if _iterable(one):
            try:
                len(one)
            except TypeError:
                logger.warning(f'No length for iterator, max_iter: {max_iter}')
                if max_iter:
                    one = islice(one, max_iter)
                    two = islice(two, max_iter)
                else:
                    logger.warning('max_iter not set... making list of all items iterator')
                    one = list(one)
                    two = list(two)

            if len(one) != len(two):
                return CmpResult(False, path, self._fmt(Mismatches.Size, one, two))

            o = list(one)
            t = list(two)
            if order:
                try:
                    o = sorted(o)
                    t = sorted(t)
                except:
                    pass

            items = []
            match = True
            for x in range(len(o)):
                r = self.compare(o[x],
                                 t[x],
                                 order=order,
                                 max_length=max_length,
                                 path=path + [x],
                                 include_matches=include_matches)
                if r:
                    items.append(r)
                    if match:
                        match = r.match
            return CmpResult(match, path, items=items) if not match or include_matches else None
        else:
            match = eq(one, two)
            diff = _str(one, two, max_length, match=match)
            return CmpResult(match, path, diff=diff) if not match or include_matches else None


def _str(o, t, max_length, match=True):
    sign = '==' if match else '!='
    o_str = str(o)
    t_str = str(t)
    if len(o_str) > max_length:
        o_str = o_str[:max_length] + ' ...'
    if len(t_str) > max_length:
        t_str = t_str[:max_length] + ' ...'
    return f'{o_str} {sign} {t_str}'


def _iterable(obj):
    try:
        iter(obj)
    except:
        return False
    else:
        return True
