# python-cmp
Produces human readable differences of dicts and lists by default.

Can be customized to output other formats in addition to to allowing for customized comparisons by type.

#### Example

```
from cmp import Cmp 

o1 = dict(a={1, 2, 3}, b=dict(c=('a', 'b'), d={42: 43, 'd': 1.1, 'e': [1, 'hello'], 'z': 26}))
o2 = dict(a={1, 2}, b=dict(c=('a',), d={42: 43, 'd': 1.1, 'e': [1, 'yo']}))
cmp = Cmp()
cmp.output_diffs(o1, o2)

```

Outputs
```
root (dict): Info: Mapping match False
	a (list): Size mismatch: 3 != 2
	b (dict): Info: Mapping match False
		c (list): Size mismatch: 2 != 1
		d (dict): Info: Mapping match False
			e (list): Info: Iterable match False
				1 (str): hello != yo
			z: Missing key: z != <Non Existent Key>
```

#### Other methods
`get_diffs` if there are differences will return a list of `CmpResult` objects.

`CmpResult` has these attributes:
```
match  boolean
path   list of keys in the path to this obj
diff   difference
type   python type
```

#### kwargs

`output_diff/get_diffs`

```
include_matches=False  # True will return a CmpResult even for items that match
order_lists=True   # Sort list before comparison 
max_length=30     # max text size (this is per item)
max_iteration=1000 # max size of list, tuples...
output=None    # output method, defaults to print (output_diff)
```
