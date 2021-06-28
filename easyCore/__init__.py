#  SPDX-FileCopyrightText: 2021 European Spallation Source <info@ess.eu>
#  SPDX-License-Identifier: BSD-3-Clause

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
