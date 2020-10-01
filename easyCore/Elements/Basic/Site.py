__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from typing import List, Union

from easyCore import np
from easyCore.Objects.Base import Descriptor, Parameter, BaseObj
from easyCore.Objects.Groups import BaseCollection
from easyCore.Elements.Basic.AtomicDisplacement import AtomicDisplacement
from easyCore.Utils.classTools import addLoggedProp
from easyCore.Utils.io.star import StarLoop

_SITE_DETAILS = {
    'label':       {
        'description': 'A unique identifier for a particular site in the crystal',
        'url':         'https://www.iucr.org/__data/iucr/cifdic_html/1/cif_core.dic/Iatom_site_label.html',
    },
    'type_symbol': {
        'description': 'A code to identify the atom species occupying this site.',
        'url':         'https://www.iucr.org/__data/iucr/cifdic_html/1/cif_core.dic/Iatom_site_type_symbol.html',
        'value':       '',
    },
    'position':    {
        'description': 'Atom-site coordinate as fractions of the unit cell length.',
        'url':         'https://www.iucr.org/__data/iucr/cifdic_html/1/cif_core.dic/Iatom_site_fract_.html',
        'value':       0,
        'fixed':       True
    },
    'occupancy':   {
        'description': 'The fraction of the atom type present at this site.',
        'url':         'https://www.iucr.org/__data/iucr/cifdic_html/1/cif_core.dic/Iatom_site_occupancy.html',
        'value':       1,
        'fixed':       True
    },
}


class Site(BaseObj):
    _CIF_CONVERSIONS = [
        ['label', 'atom_site_label'],
        ['specie', 'atom_site_type_symbol'],
        ['occupancy', 'atom_site_occupancy'],
        ['fract_x', 'atom_site_fract_x'],
        ['fract_y', 'atom_site_fract_y'],
        ['fract_z', 'atom_site_fract_z']
    ]

    def __init__(self, label: Descriptor, specie: Descriptor, occupancy: Parameter,
                 x_position: Parameter, y_position: Parameter, z_position: Parameter,
                 interface=None, **kwargs):
        # We can attach adp etc, which would be in kwargs. Filter them out...
        k_wargs = {k: kwargs[k] for k in kwargs.keys() if issubclass(kwargs[k], (Descriptor, Parameter, BaseObj))}
        kwargs = {k: kwargs[k] for k in kwargs.keys() if not issubclass(kwargs[k], (Descriptor, Parameter, BaseObj))}
        super(Site, self).__init__('site',
                                   label=label,
                                   specie=specie,
                                   occupancy=occupancy,
                                   fract_x=x_position,
                                   fract_y=y_position,
                                   fract_z=z_position,
                                   **k_wargs)
        self.interface = interface
        if self.interface is not None:
            self.interface.generate_bindings(self)

    @classmethod
    def default(cls, label: str, specie_label: str, interface=None):
        label = Descriptor('label', label, **_SITE_DETAILS['label'])
        specie = Descriptor('specie', specie_label, **_SITE_DETAILS['type_symbol'])
        occupancy = Parameter('occupancy', **_SITE_DETAILS['occupancy'])
        x_position = Parameter('fract_x', **_SITE_DETAILS['position'])
        y_position = Parameter('fract_y', **_SITE_DETAILS['position'])
        z_position = Parameter('fract_z', **_SITE_DETAILS['position'])
        return cls(label, specie, occupancy, x_position, y_position, z_position, interface=interface)

    @classmethod
    def from_pars(cls,
                  label: str,
                  specie: str,
                  occupancy: float = _SITE_DETAILS['occupancy']['value'],
                  x: float = _SITE_DETAILS['position']['value'],
                  y: float = _SITE_DETAILS['position']['value'],
                  z: float = _SITE_DETAILS['position']['value'],
                  interface=None):

        label = Descriptor('label', label, **_SITE_DETAILS['label'])
        specie = Descriptor('specie', value=specie,
                            **{k: _SITE_DETAILS['type_symbol'][k]
                               for k in _SITE_DETAILS['type_symbol'].keys()
                               if k != 'value'})

        pos = {k: _SITE_DETAILS['position'][k]
               for k in _SITE_DETAILS['position'].keys()
               if k != 'value'}

        x_position = Parameter('fract_x', value=x, **pos)
        y_position = Parameter('fract_y', value=y, **pos)
        z_position = Parameter('fract_z', value=z, **pos)
        occupancy = Parameter('occupancy', value=occupancy, **{k: _SITE_DETAILS['occupancy'][k]
                                                               for k in _SITE_DETAILS['occupancy'].keys()
                                                               if k != 'value'})

        return cls(label, specie, occupancy, x_position, y_position, z_position, interface=interface)

    def add_adp(self, adp_type: Union[str, AtomicDisplacement], **kwargs):
        if isinstance(adp_type, str):
            adp_type = AtomicDisplacement.from_pars(adp_type, interface=self.interface, **kwargs)
        self.add_component(adp_type)

    def add_component(self, component):
        key = ''
        if isinstance(component, AtomicDisplacement):
            key = 'adp'
        if not key:
            raise ValueError
        self._kwargs[key] = component
        self._borg.map.add_edge(self, component)
        self._borg.map.reset_type(component, 'created_internal')
        addLoggedProp(self, key, self.__getter(key), self.__setter(key), get_id=key, my_self=self,
                      test_class=BaseObj)

    def __repr__(self) -> str:
        return f'Atom {self.name} ({self.specie.raw_value}) @' \
               f' ({self.fract_x.raw_value}, {self.fract_y.raw_value}, {self.fract_z.raw_value})'

    @property
    def fract_coords(self) -> np.ndarray:
        """
        Get the current sites fractional co-ordinates as an array

        :return: Array containing fractional co-ordinates
        :rtype: np.ndarray
        """
        return np.array([self.fract_x.raw_value, self.fract_y.raw_value, self.fract_z.raw_value])

    def fract_distance(self, other_site: 'Site') -> float:
        """
        Get the distance between two sites

        :param other_site: Second site
        :type other_site: Site
        :return: Distance between 2 sites
        :rtype: float
        """
        return np.linalg.norm(other_site.fract_coords - self.fract_coords)

    @staticmethod
    def __getter(key: str):

        def getter(obj):
            return obj._kwargs[key]

        return getter

    @staticmethod
    def __setter(key):
        def setter(obj, value):
            if issubclass(obj._kwargs[key].__class__, Descriptor):
                obj._kwargs[key].value = value
            else:
                obj._kwargs[key] = value

        return setter


class Atoms(BaseCollection):
    def __init__(self, name: str, *args, interface=None, **kwargs):
        super(Atoms, self).__init__(name, *args, **kwargs)
        self.interface = interface
        if self.interface is not None:
            self.interface.generate_bindings(self)

    def __repr__(self) -> str:
        return f'Collection of {len(self)} sites.'

    def __getitem__(self, i: Union[int, slice]) -> Union[Parameter, Descriptor, BaseObj, 'BaseCollection']:
        if isinstance(i, str) and i in self.atom_labels:
            i = self.atom_labels.index(i)
        return super(Atoms, self).__getitem__(i)

    def append(self, item: Site):
        if not isinstance(item, Site):
            raise TypeError('Item must be a Site')
        if item.label.raw_value in self.atom_labels:
            raise AttributeError(f'An atom of name {item.label.raw_value} already exists.')
        super(Atoms, self).append(item)

    @property
    def atom_labels(self) -> List[str]:
        return [atom.label.raw_value for atom in self]

    @property
    def atom_species(self) -> List[str]:
        return [atom.specie.raw_value for atom in self]

    @property
    def atom_occupancies(self) -> np.ndarray:
        return np.array([atom.occupancy.raw_value for atom in self])

    def to_star(self) -> List[StarLoop]:
        default_items = [name[1] for name in Site._CIF_CONVERSIONS]
        adps = [hasattr(item, 'adp') for item in self]
        has_adp = any(adps)
        add_loops = []
        if has_adp:
            if all(adps):
                adp_types = [item.adp.adp_type.raw_value for item in self]
                if all(adp_types):
                    entries = []
                    for item in self:
                        entries.append(item.adp.to_star(item.label))
                    add_loops.append(StarLoop.from_StarSections(entries))
                else:
                    # Split up into types
                    adp_type_set = set(adp_types)
                    num_occ = [[adp_types.count(c), c] for c in adp_type_set]
                    num_occ.sort(reverse=True)
                    # Attach
                    for num, nam in num_occ:
                        entries = []
                        for item in self:
                            if nam == item.adp.adp_type.raw_value:
                                entries.append(item.adp.to_star(item.label))
                        add_loops.append(StarLoop.from_StarSections(entries))
            else:
                subset_items = []
                for item in self:
                    if hasattr(item, 'adp'):
                        subset_items.append(item)
                adp_types = [item.adp.adp_type.raw_value for item in subset_items]
                if all(adp_types):
                    entries = []
                    for item in subset_items:
                        entries.append(item.adp.to_star(item.label))
                    add_loops.append(StarLoop.from_StarSections(entries))
                else:
                    # Split up into types
                    adp_type_set = set(adp_types)
                    num_occ = [[adp_types.count(c), c] for c in adp_type_set]
                    num_occ.sort(reverse=True)
                    # Attach
                    for num, nam in num_occ:
                        entries = []
                        for item in subset_items:
                            if nam == item.adp.adp_type.raw_value:
                                entries.append(item.adp.to_star(item.label))
                        add_loops.append(StarLoop.from_StarSections(entries))
        loops = [StarLoop(self, default_items, exclude=['adp']), *add_loops]
        return loops

    @classmethod
    def from_string(cls, in_string: str):
        s = StarLoop.from_string(in_string, [name[0] for name in Site._CIF_CONVERSIONS])
        return s.to_class(cls, Site)
