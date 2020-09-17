import logging
from collections.abc import Mapping
from itertools import islice
from operator import eq

logger = logging.getLogger(__name__)


class Mismatches:
    Type = 'Type mismatch'
    Size = 'Size mismatch'
    MissingKey = 'Missing key'
    Info = 'Info'


class CmpResult:
    def __init__(self, match, path, the_type=None, diff=None):
        self.match = match
        self.path = path
        self.diff = diff
        self.type = the_type

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'CmpResult ({self.type}/{self.match}): {self.path}: {self.diff}'


class Cmp:

    def __init__(self, comparators=None, formatters=None):
        """
                :param comparators:
                dict:
                 type: comparator
                :param formatters:
                dict:
                 type : function(...) -> diff (a string unless something fancier is called for)
                 MismatchType:str ->  "

                """
        formatters = formatters or {}
        self.comparators = comparators or {}
        mk = '<Non Existent Key>'
        default_formatters = {Mismatches.Type: lambda o, t: f'{Mismatches.Type}: {type(o)} != {type(t)}',
                              Mismatches.Size: lambda o, t: f'{Mismatches.Size}: {len(o)} != {len(t)}',
                              Mismatches.MissingKey:
                                  lambda k1, k2: f'{Mismatches.MissingKey}: {k1 or mk} != {k2 or mk}',
                              Mismatches.Info: lambda x: f'{Mismatches.Info}: {x}'}
        default_formatters.update(formatters)
        self.formatters = default_formatters

    def _fmt(self, fmt_type, *args):
        return self.formatters[fmt_type](*args)

    def get_diffs(self,
                  one,
                  two,
                  include_matches=False,
                  order_lists=True,
                  max_length=30,
                  max_iteration=1000):
        return self._get_diffs(one,
                               two,
                               include_matches=include_matches,
                               order_lists=order_lists,
                               max_length=max_length,
                               max_iteration=max_iteration)

    #  TODO: have significant_digits arg.  This should be shorthand for a comparator
    #  TODO: handle cycles
    #  TODO: have skips by type.  Maybe match could be an enum with True/False/Skip instead of Boolean
    def _get_diffs(self,
                   one,
                   two,
                   include_matches=False,
                   order_lists=True,
                   max_length=30,
                   max_iteration=1000,
                   path=None):
        path = path if path is not None else []
        if one is two:
            logger.info('Objects are the same.  Returning match')
            return [CmpResult(True, path, diff='Same object compared')] if include_matches else []
        if type(one) != type(two):
            return [CmpResult(False, path, diff=self._fmt(Mismatches.Type, one, two))]
        comparator = self.comparators.get(type(one))
        if comparator:
            return comparator.compare(one,
                                      two,
                                      order_lists=order_lists,
                                      max_length=max_length,
                                      path=path,
                                      include_matches=include_matches)
        if isinstance(one, Mapping):
            missing_in_one = two.keys() - one.keys()
            results = []
            for k, v1 in one.items():
                if k not in two:
                    results.append(CmpResult(False, path + [k], diff=self._fmt(Mismatches.MissingKey, k, None)))
                else:
                    v2 = two.get(k)
                    r = self._get_diffs(v1,
                                        v2,
                                        order_lists=order_lists,
                                        max_length=max_length,
                                        path=path + [k],
                                        include_matches=include_matches)
                    results.extend(r)
            for k in missing_in_one:
                results.append(CmpResult(False, path + [k], diff=self._fmt(Mismatches.MissingKey, None, k)))

            match = all([x.match for x in results])
            if not match or include_matches:
                results.insert(0,
                               CmpResult(match,
                                         path,
                                         the_type=type(one).__name__,
                                         diff=self._fmt(Mismatches.Info,
                                                        f'Mapping match {match}')))
            return results
        if _iterable(one):

            if max_iteration:
                one = list(islice(one, max_iteration))
                two = list(islice(two, max_iteration))

            if len(one) != len(two):
                return [CmpResult(False, path, the_type=type(one).__name__, diff=self._fmt(Mismatches.Size, one, two))]

            o = list(one)
            t = list(two)
            if order_lists:
                try:
                    o = sorted(o)
                    t = sorted(t)
                except:
                    pass

            results = []
            for x in range(len(o)):
                r = self._get_diffs(o[x],
                                    t[x],
                                    order_lists=order_lists,
                                    max_length=max_length,
                                    path=path + [x],
                                    include_matches=include_matches)
                results.extend(r)
            match = all([x.match for x in results])
            if not match or include_matches:
                results.insert(0,
                               CmpResult(match,
                                         path,
                                         the_type=type(one).__name__,
                                         diff=self._fmt(Mismatches.Info,
                                                        f'Iterable match {match}')))
            return results
        else:
            match = eq(one, two)
            diff = _str(one, two, max_length, match=match)
            return [
                CmpResult(match, path, the_type=type(one).__name__, diff=diff)] if not match or include_matches else []

    def output_diffs(self,
                     one,
                     two,
                     include_matches=False,
                     order_lists=True,
                     max_length=30,
                     max_iteration=1000,
                     output=None):
        output = output or print
        diffs = self.get_diffs(one,
                               two,
                               include_matches=include_matches,
                               order_lists=order_lists,
                               max_length=max_length,
                               max_iteration=max_iteration)
        for d in diffs:
            prefix = '\t' * len(d.path)
            name = d.path[-1] if len(d.path) > 0 else 'root'
            t = f' ({d.type})' if d.type else ''
            output(f'{prefix}{name}{t}: {d.diff}')


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
    if isinstance(obj, str):
        return False
    try:
        iter(obj)
    except:
        return False
    else:
        return True
