#  SPDX-FileCopyrightText: 2021 easyCore contributors  <core@easyscience.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2021 Contributors to the easyCore project <https://github.com/easyScience/easyCore>

__author__ = 'github.com/wardsimon'
__version__ = '0.1.0'

import numpy as np

from easyCore.Objects.Borg import Borg
import pint
default_fitting_engine = 'lmfit'

ureg = pint.UnitRegistry()
borg = Borg()
borg.instantiate_stack()
borg.stack.enabled = False
