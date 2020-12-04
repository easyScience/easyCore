__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import weakref
from typing import Union, List

from easyCore.Utils.Hugger.Property import LoggedProperty
from easyCore.Utils.classTools import addProp
from easyCore.Utils.json import MSONable
from collections.abc import Sequence


class Virtualizes:
    """
    Virtualizes is an object which mimics what it was created with. This new object accesses all the methods and
    properties of the parent, but can not be modified. By supplying key-word arguments fields can be overwritten.

    A use case would be say for atoms. We have a unique atom, though through symmetry there are `n` in the unit cell.
    These `n` atoms are the same as the original except the position is a modification of the original.
    """

    def __init__(self, object_in, **kwargs):

        self._virtual_obj = weakref.ref(object_in)
        a_methods = dir(object_in)
        a_methods.extend(list(object_in.__dict__.keys()))
        object_methods = set(a_methods)
        known_methods = set(dir(MSONable))

        methods_to_transfer = {method for method in object_methods.symmetric_difference(known_methods)
                               if not method.startswith('__')}

        methods_override = set(kwargs.keys())
        methods_to_transfer = methods_to_transfer.symmetric_difference(methods_override)

        # Set the default methods
        for method in methods_to_transfer:
            # Note that most these are not actually methods but props
            this_prop = getattr(object_in.__class__, method, None)
            if isinstance(this_prop, (property, LoggedProperty)):
                # This covers all props
                this_obj = self.__caller_d_dict__(method)
            elif callable(this_prop):
                # This covers all methods.
                # These are stored in obj.__class__.__dict__
                this_obj = self.__caller(method)
            else:
                # These are stored in obj.__dict__
                print(method)
                continue
            addProp(self, method, fget=this_obj, fset=self.__passer())

        # Set the methods we are told to override.
        for method in methods_override:
            data = kwargs[method]
            # Data might be in the form of a dict, list or callable
            if not isinstance(data, dict):
                if isinstance(data, list):
                    # Deal with the list case data should be [fget_callable, fset_callable, fdel_callable] or
                    # length 0:n their of
                    opts = ['fget', 'fset', 'fdel']
                    new_data = {}
                    for idx, d in enumerate(data):
                        new_data[opts[idx]] = d
                    data = new_data
                else:
                    # If we are only given a callable. It's going to be a fget.
                    data = {
                        'fget': data
                    }
            addProp(self, method, **data)

    def __caller_d_dict__(self, method):
        """
        Retrieve value from an added prop

        :param method:
        :type method:
        :return:
        :rtype:
        """

        def _call_ref_(obj):
            return getattr(self._virtual_obj().__class__, method).fget(obj)

        return _call_ref_

    def __caller(self, method):
        """
        Retrieve value from a class method

        :param method:
        :type method:
        :return:
        :rtype:
        """

        def _call(obj, *args, **kwargs):
            c = getattr(self._virtual_obj().__class__, method)
            return c(obj, *args, **kwargs)
        return _call

    def __passer(self):
        """
        We do not want to throw and error if someone tries to set. Just let it go

        :return:
        :rtype:
        """

        def _passing_fn(obj, value):
            pass

        return _passing_fn

    def __repr__(self) -> str:
        old_str = self._virtual_obj().__repr__()
        if old_str[0] == '<':
            return f'<Virtual{old_str[1:]}'
        else:
            return f'Virtual{old_str}'


class VirtualizesCollection(Virtualizes, Sequence):
    """
    This class is the same as `Virtualizes` except that it can handle virtual arrays.
    """
    def __init__(self, obj_in, generator_function=None, **kwargs):
        super(VirtualizesCollection, self).__init__(obj_in, **kwargs)
        self.__virtual_store = []
        if generator_function:
            for item in obj_in:
                new_objs: List[dict] = generator_function[item]
                for new_obj in new_objs:
                    self.__virtual_store.append(Virtualizes(item, **new_obj))

    def __getitem__(self, idx: Union[int, slice]):
        """
        Get an item in the collection based on it's index.

        :param idx: index or slice of the collection.
        :type idx: Union[int, slice]
        :return: Object at index `idx`
        :rtype: Union[Parameter, Descriptor, BaseObj, 'BaseCollection']
        """
        n = len(self._virtual_obj())
        if idx > n:
            return self.__virtual_store[idx - n]
        return self._virtual_obj().__getitem__(idx)

    def __len__(self):
        return len(self._virtual_obj()) + len(self.__virtual_store)

