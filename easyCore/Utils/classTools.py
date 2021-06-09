__author__ = 'github.com/wardsimon'
__version__ = '0.1.0'

from typing import List, Tuple

from easyCore.Utils.Hugger.Property import LoggedProperty
from easyCore import borg


def addLoggedProp(inst, name, *args, **kwargs):
    cls = type(inst)
    if not hasattr(cls, '__perinstance'):
        cls = type(cls.__name__, (cls,), {})
        cls.__perinstance = True
        inst.__old_class__ = inst.__class__
        inst.__class__ = cls
    setattr(cls, name, LoggedProperty(*args, **kwargs))


def addProp(inst, name, *args, **kwargs):
    cls = type(inst)
    if not hasattr(cls, '__perinstance'):
        cls = type(cls.__name__, (cls,), {})
        cls.__perinstance = True
        inst.__old_class__ = inst.__class__
        inst.__class__ = cls
    setattr(cls, name, property(*args, **kwargs))


def removeProp(inst, name):
    cls = type(inst)
    if not hasattr(cls, '__perinstance'):
        cls = type(cls.__name__, (cls,), {})
        cls.__perinstance = True
        inst.__old_class__ = inst.__class__
        inst.__class__ = cls
    delattr(cls, name)


def generatePath(model_obj, skip_first: bool = False) -> Tuple[List[int], List[str]]:
    pars = model_obj.get_parameters()
    start_idx = 0 + int(skip_first)
    ids = []
    names = []
    model_id = borg.map.convert_id(model_obj)
    for par in pars:
        elem = borg.map.convert_id(par)
        route = borg.map.reverse_route(elem, model_id)
        objs = [getattr(borg.map.get_item_by_key(r), 'name') for r in route]
        objs.reverse()
        names.append('.'.join(objs[start_idx:]))
        ids.append(elem.int)
    return ids, names
