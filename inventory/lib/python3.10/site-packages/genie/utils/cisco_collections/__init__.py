__all__ = (
    'OrderedSet',
    'UserRange',
    'UserSet',
    'TypedSet',
    'typedset',
    'TypedDict',
    'typeddict',
)

import collections
import collections.abc
import inspect
from abc import abstractmethod

from .abc import *
from . import abc as _abc
__all__ += _abc.__all__


class OrderedSet(collections.abc.MutableSet, collections.abc.Sequence):
    '''Build an ordered collection of unique elements.

    Examples:

        ``OrderedSet()`` -> new empty OrderedSet object.

        ``OrderedSet(iterable)`` -> new OrderedSet object.

    Inspired by:
        Raymond Hettinger's OrderedSet (Python recipe)
        (http://code.activestate.com/recipes/576694/)

    Enhanced by:
        Jean-Sebastien Trottier <strottie@cisco.com>
    '''

    def __init__(self, iterable=None):
        self.end = end = []
        end += [None, end, end]  # sentinel node for doubly linked list
        self.map = {}            # item --> [item, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        '''Implement `len(self)`.'''
        return len(self.map)

    def __contains__(self, item):
        '''Implement `item in self`.'''
        return item in self.map

    def add(self, item):
        '''Add an element to a set.

        This has no effect if the element is already present.
        '''
        if item not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[item] = [item, curr, end]

    def discard(self, item):
        '''Remove an element from a set if it is a member.

        If the element is not a member, do nothing.
        '''
        try:
            item, prev, next = self.map.pop(item)
        except KeyError:
            pass
        else:
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        '''Implement `iter(self)`.'''
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        '''Implement `reversed(self)` -- return a reverse iterator over the set'''
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        '''Remove and return the first (or last) set element.

        Raises:
            KeyError: if the set is empty.
        '''
        if not self:
            raise KeyError('set is empty')
        item = self.end[1][0] if last else self.end[2][0]
        self.discard(item)
        return item

    def __reduce__(self):
        '''Return state information for pickling.'''
        return (self.__class__, (list(self),))

    def __repr__(self):
        '''Implement `repr(self)`.'''
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        '''Implement `self == other`.

        Note:
            When compared to a set, they are considered equal irrespective of
            their order.  When compared to a sequence, order is important.
        '''
        if isinstance(other, collections.abc.Set):
            # strottie: Raymond Hettinger's implementation breaks the premise
            # that two sets are equal irrespective of their order and
            # collections.Set's other comparison operators also rely on this
            # fact.
            return super().__eq__(other)
        elif isinstance(other, collections.abc.Sequence):
            # Also implement comparison with ordered sequences, where order is
            # important
            return len(self) == len(other) \
                and all(x == y for x, y in zip(self, other))
        else:
            return NotImplemented

    def __and__(self, other):
        '''Implement `self & other`.

        The relative order of items in `self` is kept.
        '''
        # collections.Set.__and__ keeps the order of other; Fix it.
        it = (item for item in self if item in other)
        return self._from_iterable(it)

    def __rand__(self, other):
        '''Implement `other & self`.

        If `other` is a sequence, the relative order of items in `other` is
        kept and a new OrderedSet is returned.  Otherwise, a simple unordered
        set is returned.
        '''
        # Collection.Set.__rand__ (3.4.2) always returns a type(self)
        it = (item for item in other if item in self)
        if isinstance(other, collections.abc.Sequence):
            # Order is kept intact
            return self._from_iterable(it)
        elif isinstance(other, collections.abc.Iterable):
            # Order is unreliable
            return set(it)
        else:
            return NotImplemented

    # collections.Set.__sub__ is fine

    def __rsub__(self, other):
        '''Implement `other - self`.

        If `other` is a sequence, the relative order of items in `other` is
        kept and a new OrderedSet is returned.  Otherwise, a simple unordered
        set is returned.
        '''
        # Collection.Set.__rsub__ (3.4.2) always returns a type(self)
        it = (item for item in other if item not in self)
        if isinstance(other, collections.abc.Sequence):
            # Order is kept intact
            return self._from_iterable(it)
        elif isinstance(other, collections.abc.Iterable):
            # Order is unreliable
            return set(it)
        else:
            return NotImplemented

    # collections.Set.__or__ is fine

    def __ror__(self, other):
        '''Implement `other | self`.

        If `other` is a sequence, the relative order of items in `other` is
        kept and a new OrderedSet is returned.  Otherwise, a simple unordered
        set is returned.
        '''
        # Collection.Set.__ror__ always returns a type(self)
        it = (e for s in (other, self) for e in s)
        if isinstance(other, collections.abc.Sequence):
            # Order is kept intact
            return self._from_iterable(it)
        elif isinstance(other, collections.abc.Iterable):
            # Order is unreliable
            return set(it)
        else:
            return NotImplemented

    # collections.Set.__xor__ is fine

    def __rxor__(self, other):
        '''Implement `other ^ self`.

        If `other` is a sequence, the relative order of items in `other` is
        kept and a new OrderedSet is returned.  Otherwise, a simple unordered
        set is returned.
        '''
        # Collection.Set.__xror__ (3.4.2) = __ror__, so order is of self;
        # Fix it.
        if isinstance(other, collections.abc.Sequence):
            # Order is kept intact
            return (self - other) | (other - self)
        elif isinstance(other, collections.abc.Iterable):
            # Order is unreliable
            return set((self - other) | (other - self))
        else:
            return NotImplemented

    def __getitem__(self, index):
        '''Implement `self[index]`.'''
        if isinstance(index, slice):
            result = []
            rng = range(*index.indices(len(self)))
            if rng.step < 0:
                # Walk backwards
                fwd = False
                rng = range(
                    len(self) - 1 - rng.start,
                    len(self) - 1 - rng.stop,
                    - rng.step)
            else:
                fwd = True
            try:
                it = iter(rng)
                nexti = next(it)
                for i, element in enumerate(self if fwd else reversed(self)):
                    if i == nexti:
                        result.append(element)
                        nexti = next(it)
            except StopIteration:
                pass
            return self._from_iterable(result)
        elif isinstance(index, int):
            if index < 0:
                # Negative index
                index += len(self)
            if index < 0 or index >= len(self):
                raise IndexError('{} index out of range'.format(
                    self.__class__.__name__))
            if index >= len(self) / 2:
                # Walk backwards, it is faster.
                fwd = False
                index = len(self) - 1 - index
            else:
                fwd = True
            for i, element in enumerate(self if fwd else reversed(self)):
                if i == index:
                    return element
            raise RuntimeError
        else:
            raise TypeError('{} indices must be integers, not {}'.format(
                self.__class__.__name__,
                index.__class__.__name__))

    def count(self, item):
        'S.count(item) -> integer -- return number of occurrences of item'
        return 1 if item in self else 0


class UserRange(Range):
    '''A complete user-defined wrapper around range objects.

    Examples:

        ``UserRange(stop)`` -> UserRange object.

        ``UserRange(start, stop[, step])`` -> UserRange object.

    Arguments:
        start: start item of the range. Defaults to 0.
        stop: stop item of the range (exclusive).
        step: step amount between items. Defaults to 1.

    Returns:
        A virtual sequence of items from `start` to `stop` by `step`.

    Attributes:
        data (range): A real range object used to store the contents of the
            UserRange class.

    '''

    def __init__(self, *args):
        if len(args) == 1:
            start = 0
            stop, = args
            step = 1
        elif len(args) == 2:
            start, stop = args
            step = 1
        elif len(args) == 3:
            start, stop, step = args
        else:
            raise TypeError(args)
        self.data = range(
            start if type(start) is int else self.item_to_int(start),
            stop if type(stop) is int else self.item_to_int(stop),
            # Let range() enforce type(step) is int
            step if type(step) is int else self.step_to_int(step),
        )
        return super().__init__()

    def item_to_int(self, item):
        '''Convert an external `item` to an `int` for the internal data range.

        Subclasses should override this method to provide custom `item` to `int` conversion.
        '''
        return int(item)

    def int_to_item(self, i):
        '''Convert an internal data range `int` to an external `item`.

        Subclasses should override this method to provide custom `int` to `item` conversion.
        '''
        return i

    def step_to_int(self, step):
        '''Convert an external `step` to an `int` for the internal data range.

        Subclasses should override this method to provide custom `step` to `int` conversion.
        '''
        return int(step)

    def int_to_step(self, step):
        '''Convert an internal data range `int` to an external `step`.

        Subclasses should override this method to provide custom `int` to `step` conversion.
        '''
        return self.int_to_item(step)

    def _item_repr(self, item):
        '''Override to customize `repr(item)`.'''
        return repr(item)

    def _step_repr(self, step):
        '''Override to customize `repr(step)`.'''
        return repr(step)

    @property
    def start(self):
        '''The start item of the range.'''
        return self.int_to_item(self.data.start)

    @property
    def stop(self):
        '''The stop item of the range (exclusive).'''
        return self.int_to_item(self.data.stop)

    @property
    def step(self):
        '''The step amount between items of the range (exclusive).'''
        return self.int_to_step(self.data.step)

    def __len__(self):
        '''Implement `len(self)`.

        Note:
            Python ranges support large number of items but the `len` function
            doesn't accept `__len__` returning numbers greater than `ssize_t`.
            A functionning implementation is provided in case of overflow so
            `__len__` actually returns if caller is willing to bypass the `len`
            builtin.
        '''
        try:
            return len(self.data)
        except OverflowError as e:
            # OverflowError: Python int too large to convert to C ssize_t

            # Implement compute_range_length / get_len_of_range here:

            lo = self.data.start
            hi = self.data.stop
            step = self.data.step

            # /* -------------------------------------------------------------
            # If step > 0 and lo >= hi, or step < 0 and lo <= hi, the range is
            # empty.
            # Else for step > 0, if n values are in the range, the last one is
            # lo + (n-1)*step, which must be <= hi-1.  Rearranging,
            # n <= (hi - lo - 1)/step + 1, so taking the floor of the RHS gives
            # the proper value.  Since lo < hi in this case, hi-lo-1 >= 0, so
            # the RHS is non-negative and so truncation is the same as the
            # floor.  Letting M be the largest positive long, the worst case
            # for the RHS numerator is hi=M, lo=-M-1, and then
            # hi-lo-1 = M-(-M-1)-1 = 2*M.  Therefore unsigned long has enough
            # precision to compute the RHS exactly.  The analysis for step < 0
            # is similar.
            # ---------------------------------------------------------------*/

            assert step != 0
            if step > 0 and lo < hi:
                return 1 + (hi - 1 - lo) // step
            elif step < 0 and lo > hi:
                return 1 + (lo - 1 - hi) // - step
            else:
                return 0

    def __getitem__(self, index):
        '''Implement `self[index]`.'''
        return self.int_to_item(self.data[index])

    def index(self, item, *args):
        '''`S.index(item, [start, [stop]])` -> integer -- return index of item.

        Raises:
            ValueError: if the item is not present.
        '''
        try:
            int_item = self.item_to_int(item)
        except (TypeError, ValueError):
            raise ValueError('%r is not in range' % (item,))
        try:
            return self.data.index(int_item, *args)
        except ValueError:
            raise ValueError('%r is not in range' % (item,))

    def __iter__(self):
        '''Implement `iter(self)`.'''
        for i in self.data:
            yield self.int_to_item(i)

    def __contains__(self, item):
        '''Implement `item in self`.'''
        try:
            int_item = self.item_to_int(item)
        except (TypeError, ValueError):
            return False
        return int_item in self.data

    def __reversed__(self):
        '''Implement `reversed(self)` -- return a reverse iterator over the range'''
        for i in reversed(self.data):
            yield self.int_to_item(i)

    def __eq__(self, other):
        '''Implement `self == other`.'''
        if type(self) is not type(other):
            return NotImplemented
        return self.data == other.data

    def __ne__(self, other):
        '''Implement `self != other`.'''
        if type(self) is not type(other):
            return NotImplemented
        return self.data != other.data

    def __repr__(self):
        '''Implement `repr(self)`.'''
        start = self.start
        stop = self.stop
        step = self.step
        if self.step_to_int(step) != 1:
            return '{}({}, {}, {})'.format(
                self.__class__.__name__,
                self._item_repr(self.start),
                self._item_repr(self.stop),
                self._step_repr(self.step))
        # Would make sense, but Python's range doesn't do this:
        #elif self.item_to_int(start) == 0:
        #    return '{}({})'.format(
        #        self.__class__.__name__,
        #        self._item_repr(self.stop))
        else:
            return '{}({}, {})'.format(
                self.__class__.__name__,
                self._item_repr(self.start),
                self._item_repr(self.stop))

    __str__ = __repr__

    def __hash__(self):
        '''Implement `hash(self)`.'''
        return hash(self.data)

    def __reduce__(self):
        '''Return state information for pickling.'''
        return (self.__class__, (self.start, self.stop, self.step))

    # From object: __format__
    # From object: __reduce_ex__
    # From object: __sizeof__
    # From Range: __subclasshook__


class UserSet(collections.abc.MutableSet):
    '''A complete user-defined wrapper around set objects.

    Examples:

        ``UserSet()`` -> new empty UserSet object.

        ``UserSet(iterable)`` -> new UserSet object.

    Attributes:
        data (set): A set range object used to store the contents of the
            UserSet class.
    '''

    # Low-level / Direct data access

    def __init__(self, iterable):
        self.data = set()
        if iterable is not None:
            self |= iterable

    def __contains__(self, item):
        '''Implement `item in self`.'''
        return item in self.data

    def __iter__(self):
        '''Implement `iter(self)`.'''
        return iter(self.data)

    def __len__(self):
        '''Implement `len(self)`.'''
        return len(self.data)

    def __reduce__(self):
        '''Return state information for pickling.'''
        return (self.__class__, (list(self),))

    def __repr__(self):
        '''Implement `repr(self)`.'''
        s = '{}('.format(
            self.__class__.__name__)
        if self:
            s += '{!r}'.format(set(self))
        s += ')'
        return s

    def add(self, item):
        '''Add an element to a set.

        This has no effect if the element is already present.
        '''
        self.data.add(item)

    def remove(self, item):
        '''Remove an element from a set.

        Raises:
            KeyError: if the item is not contained in the set.
        '''
        self.data.remove(item)

    def clear(self):
        '''Remove all elements from the set.'''
        self.data.clear()

    # Derived

    @classmethod
    def _from_iterable(cls, iterable):
        '''Return a new UserSet with elements from `iterable`.'''
        assert iterable is not None
        return cls(iterable)

    # MutableSet.__le__ -- uses __contains__
    # MutableSet.__eq__ -- uses __le__
    # MutableSet.__lt__ -- uses __le__
    # MutableSet.__ne__ -- uses __eq__
    # MutableSet.__ge__ -- uses other.__le__
    # MutableSet.__gt__ -- uses other.__lt__

    # MutableSet.__and__ -- uses __contains__
    # MutableSet.__or__ -- uses _from_iterable
    # MutableSet.__sub__ -- uses _from_iterable, other.__contains__
    # MutableSet.__xor__ -- uses __sub__, __or__, other.__sub__

    # MutableSet.__iand__ -- uses __sub__, discard
    # MutableSet.__ior__ -- uses add
    # MutableSet.__isub__ -- uses clear, discard
    # MutableSet.__ixor__ -- uses clear, discard, add

    def discard(self, item):
        '''Remove an element from the set if it is present.'''
        try:
            self.remove(item)
        except KeyError:
            pass

    # MutableSet.pop -- uses iter

    def copy(self):
        '''Return a shallow copy of the set.'''
        return self._from_iterable(self)

    def difference(self, *args):
        '''`S.difference(other, ...)` -- Return a new set with elements in the
        set that are not in the others.
        '''
        ret = self.copy()
        ret.difference_update(*args)
        return ret

    def difference_update(self, *args):
        '''`S.difference_update(other, ...)` -- Update the set, removing
        elements found in others.
        '''
        for arg in args:
            self -= arg

    def intersection(self, *args):
        '''`S.intersection(other, ...)` -- Return a new set with elements
        common to the set and all others.
        '''
        ret = self.copy()
        ret.intersection_update(*args)
        return ret

    def intersection_update(self, *args):
        '''`S.intersection_update(other, ...)` -- Update the set, keeping only
        elements found in it and all others.
        '''
        for arg in args:
            self ^= arg

    # MutableSet.isdisjoint -- uses __contains__

    def issubset(self, other):
        '''`S.issubset(other)` <==> `S <= other` -- Test whether every
        element in the set is in `other`.
        '''
        return self <= other

    def issuperset(self, other):
        '''`S.issuperset(other)` <==> `S >= other` -- Test whether every
        element in `other` is in the set.
        '''
        return self >= other

    def symmetric_difference(self, other):
        '''`S.symmetric_difference(other)` <==> `S ^ other` -- Return a new set
        with elements in either the set or `other` but not both.
        '''
        return self ^ other

    def symmetric_difference_update(self, other):
        '''`S.symmetric_difference_update(other)` <==> `S ^= other` -- Update
        the set, keeping only elements found in either the set or `other`, but
        not in both.
        '''
        self ^= other

    def union(self, *args):
        '''`S.union(other, ...)` <==> `S | other | ...` -- Return a new set
        with elements from the set and all others.'''
        ret = self.copy()
        ret.update(*args)
        return ret

    def update(self, *args):
        '''`S.update(other, ...)` <==> `S |= other | ...` -- Update the set,
        adding elements from all others.
        '''
        for arg in args:
            self |= arg

    # Not supported:
    #     __rand__
    #     __ror__
    #     __rsub__
    #     __rxor__


class TypedSet(UserSet):
    '''Abstract class to implement set objects with strong type-checking.'''

    @abstractmethod
    def _sanitize_value(self, item):
        '''Implements type-checking or transformation of items.

        Override this method in derived classes to implement type-checking of
        items or to perform transformation to make items suitable to be
        included in the set.

        Implementation must return the possibly-transformed item or raise
        one of TypeError or ValueError to indicate that the item is unsuitable.
        '''
        raise NotImplementedError

    def __contains__(self, item):
        '''Implement `item in self`.'''
        item = self._sanitize_value(item)
        return super().__contains__(item)

    def add(self, item):
        '''Add an element to a set.

        This has no effect if the element is already present.
        '''
        item = self._sanitize_value(item)
        super().add(item)

    def remove(self, item):
        '''Remove an element from a set.

        Raises:
            KeyError: if the item is not contained in the set.
        '''
        item = self._sanitize_value(item)
        super().remove(item)


class typedset(TypedSet):
    '''`typeset(callable[, ...])` --> set with items verified by `callable`.

    The callable is called to type-check or transform every item to be included
    in the set.
    '''

    _sanitize_value = None

    def __init__(self, callable, iterable=None):
        callable_ = callable
        callable = __builtins__['callable']
        if not callable_ or not callable(callable_):
            raise TypeError('first argument must be callable')
        self._sanitize_value = callable_

        super().__init__(iterable)

    def __reduce__(self):
        '''Return state information for pickling.'''
        return (self.__class__, (self._sanitize_value, list(self)))

    def __repr__(self):
        '''Implement `repr(self)`.'''
        s = '{}({}'.format(
            self.__class__.__name__,
            self._sanitize_value.__name__
            if inspect.isclass(self._sanitize_value)
            else repr(self._sanitize_value))
        if self:
            s += ', {!r}'.format(set(self))
        s += ')'
        return s

    def _from_iterable(self, iterable):
        '''Return a new typedset with elements from `iterable`.'''
        assert iterable is not None
        return self.__class__(self._sanitize_value, iterable)


class TypedDict(collections.UserDict):
    '''Class to implement dict objects with strong type-checking.

    Sub-classes are encouraged to redefine the _sanitize_key, _sanitize_value,
    _assert_key_allowed, and _assert_value_allowed methods to suit their needs.
    '''

    def __contains__(self, key):
        '''Implement `key in self`.

        They key is sanitized such that it is looked up in the expected format.
        '''

        key = self._sanitize_key(key)
        return super().__contains__(key)

    def __delitem__(self, key):
        '''Implement `del self[key]`.

        They key is sanitized such that it is looked up in the expected format.
        '''
        key = self._sanitize_key(key)
        return super().__delitem__(key)

    def __getitem__(self, key):
        '''Implement `self[key]`.

        They key is sanitized such that it is looked up in the expected format.
        '''
        key = self._sanitize_key(key)
        return super().__getitem__(key)

    def __setitem__(self, key, item):
        '''Implement `self[key] = item`.

        They key and item value are sanitized and only allowed ones are
        permitted.

        Raises:
            KeyError: The key is not allowed.
            TypeError or ValueError: The item value is not allowed.
        '''
        key = self._sanitize_key(key)
        self._assert_key_allowed(key)
        item = self._sanitize_value(item)
        self._assert_value_allowed(item)
        return super().__setitem__(key, item)

    def _sanitize_key(self, key):
        '''Default key sanitizer method.

        Default implementation does nothing.

        Sub-classes are encouraged to redefine this method to suit their needs.

        Implementation is expected to attempt conversion of the key argument
        into appropriate types for keying into the dictionary. If conversion is
        not possible or not desired, the original key should be returned
        unchanged without raising an exception.

        Returns:
            key
        '''
        return key

    def _sanitize_value(self, item):
        '''Default item value sanitizer method.

        Default implementation does nothing.

        Implementation is expected to attempt conversion of the item argument
        into appropriate types for storing into the dictionary. If conversion
        is not possible or not desired, the original item should be returned
        unchanged without raising an exception.

        Returns:
            item
        '''
        return item

    def _assert_key_allowed(self, key):
        '''Default key assertion method.

        Default implementation does nothing.

        Implementation is expected to raise a KeyError exception if the key is
        not allowed (such as an undesired value or type.)

        Returns:
            None
        '''
        pass

    def _assert_value_allowed(self, item):
        '''Default item value assertion method.

        Default implementation does nothing.

        Implementation is expected to raise a TypeError or ValueError exception
        if the item value is not allowed (such as an undesired value or type.)

        Returns:
            None
        '''
        pass

    __marker = object()

    def pop(self, key, default=__marker):
        '''`self.pop(key[, default]) -> item`, remove specified key and return
        the corresponding item.

        Returns:
            item or default

        Raises:
            KeyError: If key is not found and default is not provided.
        '''
        # If __missing__ is implemented, UserDict's pop (inherited from
        # MutableMapping) does not behave properly and missing items are
        # instanciated and popped immediately. This is a behavior differs
        # from defaultdict/dict's and is corrected here.
        key = self._sanitize_key(key)
        if default is self.__marker:
            return self.data.pop(key)
        else:
            return self.data.pop(key, default)

    def setdefault(self, key, default=None):
        '''self.setdefault(key[, default]) -> self.get(key, default), also set
        self[key]=default if key not in self.'''
        # If __missing__ is implemented, UserDict's setdefault (inherited from
        # MutableMapping) does not behave properly and missing items are
        # instanciated instead of being set to the requested default value.
        # This is a behavior differs from defaultdict/dict's and is corrected
        # here.

        # Sanitize once to avoid 3 costly conversions in the worst case.
        key = self._sanitize_key(key)
        if key not in self:
            self[key] = default
        # Force a lookup even in default's case to return the sanitized item.
        return self[key]

    @classmethod
    def fromkeys(cls, iterable, value=None):
        if iterable:
            # Sanitize once to avoid many costly conversions.
            value = cls._sanitize_value(value)
        return super().fromkeys(iterable, value)


class typeddict(TypedDict):
    '''`typedict((key_callable, value_callable)[, ...])` --> dict with keys and
    item values verified by `key_callable` and `value_callable`, respectively.

    The callables are called to type-check or transform every key and item
    value to be included in the dict. If either callable is None, no respective
    specific type-checking is done.
    '''

    def __init__(self, callables, dict=None, **kwargs):
        key_callable, value_callable = callables
        if key_callable is not None:
            if not callable(key_callable):
                raise TypeError('key verifier argument must be callable')
            self._sanitize_key = key_callable
        if value_callable is not None:
            if not callable(value_callable):
                raise TypeError('value verifier argument must be callable')
            self._sanitize_value = value_callable

        super().__init__(dict, **kwargs)

    def __reduce__(self):
        '''Return state information for pickling.'''
        return (self.__class__, (
            (self.__dict__.get('_sanitize_key', None),
             self.__dict__.get('_sanitize_value', None)),
            dict(self)))

    def __repr__(self):
        '''Implement `repr(self)`.'''

        def _format_sanitizer(v):
            return v.__name__ if inspect.isclass(v) else repr(v)

        s = '{}(({}, {})'.format(
            self.__class__.__name__,
            _format_sanitizer(self.__dict__.get('_sanitize_key', None)),
            _format_sanitizer(self.__dict__.get('_sanitize_value', None)),
        )
        if self:
            s += ', {!r}'.format(dict(self))
        s += ')'
        return s

    def _from_iterable(self, iterable):
        '''Return a new typeddict with elements from `iterable`.'''
        assert iterable is not None
        return self.__class__(
            (self.__dict__.get('_sanitize_key', None),
             self.__dict__.get('_sanitize_value', None),
             ),
            iterable)

# vim: ft=python et sw=4
