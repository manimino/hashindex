# Filtered

Python container that pre-filters objects by attribute value. 

Provides fast (typically <1ms) lookup by any combination of attributes.

`pip install filtered`

[![tests Actions Status](https://github.com/manimino/filtered/workflows/tests/badge.svg)](https://github.com/manimino/filtered/actions)
[![Coverage - 100%](https://img.shields.io/static/v1?label=Coverage&message=100%&color=2ea44f)](test/cov.txt)

### Usage:

```
from filtered import Filtered
f = Filtered(objects, attributes)
objs = f.find(match={attr1: values, ...}, exclude={attr2: values, ...})
```

Filtered can hold any Python object: class instances, namedtuples, dicts, strings, floats, ints, etc.

Attributes can be actual object attributes, or they can be functions of the object. Functions
allow lookup of nested and derived attributes. See examples below.

There are two classes available.
 - Filtered: can `add()` and `remove()` objects.
 - FrozenFiltered: much faster performance and lower memory cost, but can't be changed after creation.

____

## Examples

### Dicts

```
from filtered import Filtered

objects = [
    {'order': 1, 'size': 'regular', 'topping': 'smothered'}, 
    {'order': 2, 'size': 'regular', 'topping': 'diced'}, 
    {'order': 3, 'size': 'large', 'topping': 'covered'},
    {'order': 4, 'size': 'triple', 'topping': 'chunked'}
]

f = Filtered(objects, on=['size', 'topping'])

f.find(match={'size': 'regular', 'topping': 'smothered'})  # returns order 1

f.find(
    match={'size': ['regular', 'large']},  # match 'regular' or 'large' sizes
    exclude={'topping': 'diced'}         # exclude where topping is 'covered'
)  # returns orders 1 and 3
```

### Object with nested attributes

```
from filtered import Filtered

class Order:
    def __init__(self, num, size, toppings):
        self.num = num
        self.size = size
        self.toppings = toppings
    
    def __repr__(self):
        return f"{self.num}, {self.size}, {self.toppings}"
    
objects = [
    Order(1, 'regular', ['scattered', 'smothered', 'covered']),
    Order(2, 'large', ['scattered', 'covered', 'peppered']),
    Order(3, 'large', ['scattered', 'diced', 'chunked']),
    Order(4, 'triple', ['all the way']),
]

def has_cheese(obj):
    return 'covered' in obj.toppings or 'all the way' in obj.toppings

f = FrozenFiltered(objects, ['size', has_cheese])

f.find({has_cheese: True})  # returns orders 1, 2 and 4
```

### Strings

```
from filtered import FrozenFiltered

objects = ['mushrooms', 'peppers', 'onions']

def o_count(obj):
    return obj.count('o')

f = FrozenFiltered(objects, [o_count, len])
f.find({len: 6})       # returns ['onions']
f.find({o_count: 2})  # returns ['mushrooms', 'onions']
```

### Recipes
 
 - [Auto-updating](examples/update.py) - Keep Filtered updated when attribute values change
 - [Wordle solver](examples/wordle.ipynb) - Use `functools.partials` to make many attribute functions
 - [Collision detection](examples/collision.py) - Find objects based on type and proximity (grid-based)
 - [Percentiles](examples/percentile.py) - Find by percentile (median, p99, etc.)

____

## Performance


### FrozenFiltered



### Filtered


____

## How it works

Attribute values are stored by their hash, either in dicts (Filtered) or numpy 
arrays (FrozenHashFilter). So values don't need to be comparable by greater than / less than, they only need to be 
hashable. This maximizes flexibility.

For each attribute value, the `id` of each matching object is stored. During `find`, these IDs are retrieved as sets 
(Filtered) or sorted numpy arrays (FrozenHashFilter). Set operations such as intersection are then used to find the 
objects that fit all constraints.

____
