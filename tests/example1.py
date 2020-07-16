__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import numpy as np
from easyCore.Objects.Base import Parameter, BaseObj
from easyCore.Fitting.Fitting import Fitter

# This is a simple example of creating an object which has fitable parameters

b = BaseObj('line',
            m=Parameter('m', 1),
            c=Parameter('c', 1))


def fit_fun(x):
    # In the real case we would gust call the evaluation fn without reference to the BaseObj
    return b.c.raw_value + b.m.raw_value * x


f = Fitter.fitting_engine(b, fit_fun)

x = np.array([1, 2, 3])
y = np.array([2, 4, 6]) - 1

f_res = f.fit(x, y)

print(f_res.fit_report())
