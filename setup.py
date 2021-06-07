
# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


import os.path

readme = ''
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, 'README.rst')
if os.path.exists(readme_path):
    with open(readme_path, 'rb') as stream:
        readme = stream.read().decode('utf8')


setup(
    long_description=readme,
    name='easyCore',
    version='0.0.1',
    description='Generic logic for easyScience libraries',
    python_requires='==3.*,>=3.6.0,>=3.6.1',
    project_urls={"documentation": "https://github.com/easyScience/easyCore", "homepage": "https://github.com/easyScience/easyCore"},
    author='Simon Ward',
    license='GPL-3.0',
    classifiers=['Development Status :: 3 - Alpha', 'Intended Audience :: Developers', 'Topic :: Scientific/Engineering :: Physics', 'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)', 'Programming Language :: Python :: 3.6, 3.7, 3.8, 3.9'],
    packages=['easyCore', 'easyCore.Datasets', 'easyCore.Elements', 'easyCore.Elements.Basic', 'easyCore.Elements.HigherLevel', 'easyCore.Fitting', 'easyCore.Objects', 'easyCore.Symmetry', 'easyCore.Utils', 'easyCore.Utils.Hugger', 'easyCore.Utils.io'],
    package_dir={"": "."},
    package_data={"easyCore.Elements": ["*.json"], "easyCore.Symmetry": ["*.json"]},
    install_requires=['asteval==0.*,>=0.9.23', 'bumps==0.*,>=0.8.0', 'dfo-ls==1.*,>=1.2.1', 'lmfit==1.*,>=1.0.0', 'numpy==1.*,>=1.19.0', 'pint==0.*,>=0.16.0', 'uncertainties==3.*,>=3.1.0', 'xarray==0.*,>=0.16.2'],
)
