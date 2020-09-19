__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

from collections import Set
from numbers import Number

import pytest

from typing import List, Tuple
from easyCore.Fitting.Constraints import NumericConstraint, ObjConstraint
from easyCore.Objects.Base import Parameter

@pytest.fixture
def twoPars() -> Tuple[List[Parameter], List[int]]:
    return [Parameter('a', 1), Parameter('b', 2)], [1, 2]


@pytest.fixture
def threePars() -> Tuple[List[Parameter], List[int]]:
    ps, vs = twoPars()
    ps.append(Parameter('c', 3))
    vs.append(3)
    return ps, vs


def test_NumericConstraints_Equals(twoPars):

    value = 1
    c = NumericConstraint(twoPars[0][0], '==', value)
    c()
    assert twoPars[0][0].raw_value == twoPars[1][0]
    c = NumericConstraint(twoPars[0][1], '==', value)
    c()
    assert twoPars[0][1].raw_value == value


def test_NumericConstraints_Greater(twoPars):
    value = 1.5
    c = NumericConstraint(twoPars[0][0], '>', value)
    c()
    assert twoPars[0][0].raw_value == value
    c = NumericConstraint(twoPars[0][1], '>', value)
    c()
    assert twoPars[0][1].raw_value == twoPars[1][1]


def test_NumericConstraints_Less(twoPars):
    value = 1.5
    c = NumericConstraint(twoPars[0][0], '<', value)
    c()
    assert twoPars[0][0].raw_value == twoPars[1][0]
    c = NumericConstraint(twoPars[0][1], '<', value)
    c()
    assert twoPars[0][1].raw_value == value


@pytest.mark.parametrize('operator', [None, 1, 2, 3, 4.5])
def test_ObjConstraintMultiply(twoPars, operator):
    if operator is None:
        operator = 1
        operator_str = ''
    else:
        operator_str = f'{operator}*'
    c = ObjConstraint(twoPars[0][0], operator_str, twoPars[0][1])
    c()
    assert twoPars[0][0].raw_value == operator*twoPars[1][1]


@pytest.mark.parametrize('operator', [1, 2, 3, 4.5])
def test_ObjConstraintDivide(twoPars, operator):
    operator_str = f'{operator}/'
    c = ObjConstraint(twoPars[0][0], operator_str, twoPars[0][1])
    c()
    assert twoPars[0][0].raw_value == operator/twoPars[1][1]