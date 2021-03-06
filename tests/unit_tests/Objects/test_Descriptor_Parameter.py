__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from copy import deepcopy
from typing import List

import pytest
import numpy as np
from easyCore.Objects.Base import Descriptor, Parameter, ureg, Q_


@pytest.fixture
def instance(request):
    def class_creation(*args, **kwargs):
        return request.param(*args, **kwargs)

    return class_creation


def _generate_inputs():
    # These are the parameters which will always be present
    basic = {
        'name':  'test',
        'value': 1
    }
    basic_result = {
        'name':      basic['name'],
        'raw_value': basic['value'],
    }
    # These will be the optional parameters
    advanced = {'units':        ['cm', 'mm', 'kelvin'],
                'description':  'This is a test',
                'url':          'https://www.whatever.com',
                'display_name': "\Chi",
                }
    advanced_result = {
        'units':        {'name': 'unit', 'value': ['centimeter', 'millimeter', 'kelvin']},
        'description':  {'name': 'description', 'value': advanced['description']},
        'url':          {'name': 'url', 'value': advanced['url']},
        'display_name': {'name': 'display_name', 'value': advanced['display_name']}
    }

    temp = [([[basic['name'], basic['value']], {}], basic_result),
            ([[], basic], basic_result)]

    def create_entry(base, key, value, ref, ref_key=None):
        this_temp = deepcopy(base)
        for item in base:
            test, res = item
            new_opt = deepcopy(test[1])
            new_res = deepcopy(res)
            if ref_key is None:
                ref_key = key
            new_res[ref_key] = ref
            new_opt[key] = value
            this_temp.append(([test[0], new_opt], new_res))
        return this_temp

    for add_opt in advanced.keys():
        if isinstance(advanced[add_opt], list):
            for idx, item in enumerate(advanced[add_opt]):
                temp = create_entry(temp, add_opt, item,
                                    advanced_result[add_opt]['value'][idx],
                                    ref_key=advanced_result[add_opt]['name'])
        else:
            temp = create_entry(temp, add_opt, advanced[add_opt],
                                advanced_result[add_opt]['value'],
                                ref_key=advanced_result[add_opt]['name'])
    return temp


@pytest.mark.parametrize('instance', (Descriptor, Parameter), indirect=True)
@pytest.mark.parametrize("element, expected", _generate_inputs())
def test_item_creation(instance, element: List, expected: dict):
    d = instance(*element[0], **element[1])
    for field in expected.keys():
        ref = expected[field]
        obtained = getattr(d, field)
        if isinstance(obtained, (ureg.Unit, Q_)):
            obtained = str(obtained)
        assert obtained == ref


@pytest.mark.parametrize('element, expected', [('', '1 dimensionless'),
                                               ('cm', '1 centimeter'),
                                               ('mm', '1 millimeter'),
                                               ('kelvin', '1 kelvin')])
def test_Descriptor_value_get(element, expected):
    d = Descriptor('test', 1, units=element)
    assert str(d.value) == expected


@pytest.mark.parametrize('element, expected', [('', '(1.0 +/- 0) dimensionless'),
                                               ('cm', '(1.0 +/- 0) centimeter'),
                                               ('mm', '(1.0 +/- 0) millimeter'),
                                               ('kelvin', '(1.0 +/- 0) kelvin')])
def test_Parameter_value_get(element, expected):
    d = Parameter('test', 1, units=element)
    assert str(d.value) == expected


@pytest.mark.parametrize('instance', (Descriptor, Parameter), indirect=True)
def test_item_value_set(instance):
    d = instance('test', 1)
    d.value = 2
    assert d.raw_value == 2
    d = instance('test', 1, units='kelvin')
    d.value = 2
    assert d.raw_value == 2
    assert str(d.unit) == 'kelvin'


@pytest.mark.parametrize('instance', (Descriptor, Parameter), indirect=True)
def test_item_unit_set(instance):
    d = instance('test', 1)
    d.unit = 'kg'
    assert str(d.unit) == 'kilogram'

    d = instance('test', 1, units='kelvin')
    d.unit = 'cm'
    assert str(d.unit) == 'centimeter'


@pytest.mark.parametrize('instance', (Descriptor, Parameter), indirect=True)
def test_item_convert_unit(instance):
    d = instance('test', 273, units='kelvin')
    d.convert_unit('degree_Celsius')
    assert pytest.approx(d.raw_value, -0.149)


@pytest.mark.parametrize('conv_unit, data_in, result', [('degree_Celsius', {'min': 0}, {'min': -273.149, 'raw_value': -0.149}),
                                                        ('degree_Celsius', {'max': 500}, {'max': 773.149, 'raw_value': -0.149}),
                                                        ('degree_Celsius', {'error': 0.1}, {'error': 0.1, 'raw_value': -0.149}),
                                                        ('degree_Celsius', {'min': 0, 'max': 500, 'error': 0.1},
                                                         {'min': -273.149, 'max': 773.149, 'error': 0.1, 'raw_value': -0.149}),
                                                        ('degree_Fahrenheit', {'min': 0}, {'min': -459.67, 'raw_value': 31.729}),
                                                        ('degree_Fahrenheit', {'max': 500}, {'max': 440.33, 'raw_value': 31.729}),
                                                        ('degree_Fahrenheit', {'error': 0.1}, {'error': 0.18, 'raw_value': 31.729}),
                                                        ('degree_Fahrenheit', {'min': 0, 'max': 500, 'error': 0.1},
                                                         {'min': -459.67, 'max': 440.33, 'error': 0.18, 'raw_value': 31.729})
                                                        ],
                         ids=['min_testC', 'max_testC', 'error_testC', 'combined_testC',
                              'min_testF', 'max_testF', 'error_testF', 'combined_testF'])
def test_parameter_advanced_convert_unit(conv_unit: str, data_in: dict, result: dict):
    d = Parameter('test', 273, units='kelvin', **data_in)
    d.convert_unit(conv_unit)
    for key in result.keys():
        assert pytest.approx(getattr(d, key), result[key])


@pytest.mark.parametrize('instance', (Descriptor, Parameter), indirect=True)
def test_item_compatible_units(instance):
    reference = ['degree_Fahrenheit',
                 'kelvin',
                 'atomic_unit_of_temperature',
                 'degree_Celsius',
                 'degree_Rankine',
                 'planck_temperature',
                 'degree_Reaumur']
    d = instance('test', 273, units='kelvin')
    obtained = d.compatible_units
    from unittest import TestCase
    TestCase().assertCountEqual(reference, obtained)


def test_descriptor_repr():
    d = Descriptor('test', 1)
    assert repr(d) == f'<{d.__class__.__name__} \'test\' = 1>'
    d = Descriptor('test', 1, units='cm')
    assert repr(d) == f'<{d.__class__.__name__} \'test\' = 1 centimeter>'


def test_parameter_repr():
    d = Parameter('test', 1)
    assert repr(d) == f'<{d.__class__.__name__} \'test\' = 1.0+/-0, bounds=[-inf:inf]>'
    d = Parameter('test', 1, units='cm')
    assert repr(d) == f'<{d.__class__.__name__} \'test\' = 1.0+/-0 centimeter, bounds=[-inf:inf]>'

    d = Parameter('test', 1, fixed=True)
    assert repr(d) == f'<{d.__class__.__name__} \'test\' = 1.0+/-0 (fixed), bounds=[-inf:inf]>'
    d = Parameter('test', 1, units='cm', fixed=True)
    assert repr(d) == f'<{d.__class__.__name__} \'test\' = 1.0+/-0 centimeter (fixed), bounds=[-inf:inf]>'


def test_descriptor_as_dict():
    d = Descriptor('test', 1)
    result = d.as_dict()
    expected = {'@module':      'easyCore.Objects.Base',
                '@class':       'Descriptor',
                '@version':     '0.0.1',
                'name':         'test',
                'value':        1,
                'units':        'dimensionless',
                'description':  '',
                'url':          '',
                'display_name': 'test',
                'callback':     None}
    for key in expected.keys():
        if key == 'callback':
            continue
        assert result[key] == expected[key]


def test_parameter_as_dict():
    d = Parameter('test', 1)
    result = d.as_dict()
    expected = {'@module':  'easyCore.Objects.Base',
                '@class':   'Parameter',
                '@version': '0.0.1',
                'name':     'test',
                'value':    1.0,
                'error':    0.0,
                'min':      -np.inf,
                'max':      np.inf,
                'fixed':    False,
                'units':    'dimensionless'}
    for key in expected.keys():
        if key == 'callback':
            continue
        assert result[key] == expected[key]

    # Check that additional arguments work
    d = Parameter('test', 1, units='km', url='https://www.boo.com')
    result = d.as_dict()
    expected = {'@module':  'easyCore.Objects.Base',
                '@class':   'Parameter',
                '@version': '0.0.1',
                'name':     'test',
                'units':    'kilometer',
                'value':    1.0,
                'error':    0.0,
                'min':      -np.inf,
                'max':      np.inf,
                'fixed':    False,
                'url':      'https://www.boo.com'}
    for key in expected.keys():
        if key == 'callback':
            continue
        assert result[key] == expected[key]


@pytest.mark.parametrize('reference, constructor', ([{'@module':      'easyCore.Objects.Base',
                                                      '@class':       'Descriptor',
                                                      '@version':     '0.0.1',
                                                      'name':         'test',
                                                      'value':        1,
                                                      'units':        'dimensionless',
                                                      'description':  '',
                                                      'url':          '',
                                                      'display_name': 'test',
                                                      'callback':     None}, Descriptor],
                                                    [{'@module':  'easyCore.Objects.Base',
                                                      '@class':   'Parameter',
                                                      '@version': '0.0.1',
                                                      'name':     'test',
                                                      'units':    'kilometer',
                                                      'value':    1.0,
                                                      'error':    0.0,
                                                      'min':      -np.inf,
                                                      'max':      np.inf,
                                                      'fixed':    False,
                                                      'url':      'https://www.boo.com'}, Parameter]),
                         ids=['Descriptor', 'Parameter'])
def test_item_from_dict(reference, constructor):
    d = constructor.from_dict(reference)
    for key, item in reference.items():
        if key == 'callback' or key.startswith('@'):
            continue
        if key == 'units':
            key = 'unit'
        if key == 'value':
            key = 'raw_value'
        obtained = getattr(d, key)
        if isinstance(obtained, (ureg.Unit, Q_)):
            obtained = str(obtained)
        assert obtained == item


@pytest.mark.parametrize('construct', ({'@module':      'easyCore.Objects.Base',
                                        '@class':       'Descriptor',
                                        '@version':     '0.0.1',
                                        'name':         'test',
                                        'value':        1,
                                        'units':        'dimensionless',
                                        'description':  '',
                                        'url':          '',
                                        'display_name': 'test',
                                        'callback':     None},
                                       {'@module':  'easyCore.Objects.Base',
                                        '@class':   'Parameter',
                                        '@version': '0.0.1',
                                        'name':     'test',
                                        'units':    'kilometer',
                                        'value':    1.0,
                                        'error':    0.0,
                                        'min':      -np.inf,
                                        'max':      np.inf,
                                        'fixed':    False,
                                        'url':      'https://www.boo.com'}), ids=['Descriptor', 'Parameter'])
def test_item_from_MontyDecoder(construct):
    from easyCore.Utils.json import MontyDecoder
    d = MontyDecoder().process_decoded(construct)
    assert d.__class__.__name__ == construct['@class']
    for key, item in construct.items():
        if key == 'callback' or key.startswith('@'):
            continue
        if key == 'units':
            key = 'unit'
        if key == 'value':
            key = 'raw_value'
        obtained = getattr(d, key)
        if isinstance(obtained, (ureg.Unit, Q_)):
            obtained = str(obtained)
        assert obtained == item


@pytest.mark.parametrize('value', (-np.inf, 0, 1.0, 2147483648, np.inf))
def test_parameter_min(value):
    d = Parameter('test', -0.1)
    if d.raw_value < value:
        with pytest.raises(ValueError):
            d.min = value
    else:
        d.min = value
        assert d.min == value


@pytest.mark.parametrize('value', [-np.inf, 0, 1.1, 2147483648, np.inf])
def test_parameter_max(value):
    d = Parameter('test', 2147483649)
    if d.raw_value > value:
        with pytest.raises(ValueError):
            d.max = value
    else:
        d.max = value
        assert d.max == value


@pytest.mark.parametrize('value', [True, False, 5])
def test_parameter_fixed(value):
    d = Parameter('test', -np.inf)
    if isinstance(value, bool):
        d.fixed = value
        assert d.fixed == value
    else:
        with pytest.raises(ValueError):
            d.fixed = value


@pytest.mark.parametrize('value', (-np.inf, -0.1, 0, 1.0, 2147483648, np.inf))
def test_parameter_error(value):
    d = Parameter('test', 1)
    if value >= 0:
        d.error = value
        assert d.error == value
    else:
        with pytest.raises(ValueError):
            d.error = value


def _generate_advanced_inputs():
    temp = _generate_inputs()
    # These will be the optional parameters
    advanced = {'error': 1.0,
                'min':   -0.1,
                'max':   2147483648,
                'fixed': False
                }
    advanced_result = {
        'error': {'name': 'error', 'value': advanced['error']},
        'min':   {'name': 'min', 'value': advanced['min']},
        'max':   {'name': 'max', 'value': advanced['max']},
        'fixed': {'name': 'fixed', 'value': advanced['fixed']}
    }

    def create_entry(base, key, value, ref, ref_key=None):
        this_temp = deepcopy(base)
        for item in base:
            test, res = item
            new_opt = deepcopy(test[1])
            new_res = deepcopy(res)
            if ref_key is None:
                ref_key = key
            new_res[ref_key] = ref
            new_opt[key] = value
            this_temp.append(([test[0], new_opt], new_res))
        return this_temp

    for add_opt in advanced.keys():
        if isinstance(advanced[add_opt], list):
            for idx, item in enumerate(advanced[add_opt]):
                temp = create_entry(temp, add_opt, item,
                                    advanced_result[add_opt]['value'][idx],
                                    ref_key=advanced_result[add_opt]['name'])
        else:
            temp = create_entry(temp, add_opt, advanced[add_opt],
                                advanced_result[add_opt]['value'],
                                ref_key=advanced_result[add_opt]['name'])
    return temp


@pytest.mark.parametrize("element, expected", _generate_advanced_inputs())
def test_parameter_advanced_creation(element, expected):
    if len(element[0]) > 0:
        value = element[0][1]
    else:
        value = element[1]['value']
    if 'min' in element[1].keys():
        if element[1]['min'] > value:
            with pytest.raises(ValueError):
                d = Parameter(*element[0], **element[1])
    elif 'max' in element[1].keys():
        if element[1]['max'] < value:
            with pytest.raises(ValueError):
                d = Parameter(*element[0], **element[1])
    else:
        d = Parameter(*element[0], **element[1])
        for field in expected.keys():
            ref = expected[field]
            obtained = getattr(d, field)
            if isinstance(obtained, (ureg.Unit, Q_)):
                obtained = str(obtained)
            assert obtained == ref
