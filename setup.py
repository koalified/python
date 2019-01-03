#!/usr/bin/env python
"""Defines the setup instructions for koalified"""
import glob
import os
import subprocess
import sys
from os import path

from setuptools import Extension, find_packages, setup
from setuptools.command.test import test as TestCommand

MYDIR = path.abspath(os.path.dirname(__file__))
JYTHON = 'java' in sys.platform
PYPY = bool(getattr(sys, 'pypy_version_info', False))
CYTHON = False
if not PYPY and not JYTHON:
    try:
        from Cython.Distutils import build_ext
        CYTHON = True
    except ImportError:
        pass

cmdclass = {}
ext_modules = []
if CYTHON:
    def list_modules(dirname):
        filenames = glob.glob(path.join(dirname, '*.py'))

        module_names = []
        for name in filenames:
            module, ext = path.splitext(path.basename(name))
            if module != '__init__':
                module_names.append(module)

        return module_names

    ext_modules = [
        Extension('koalified.' + ext, [path.join('koalified', ext + '.py')])
        for ext in list_modules(path.join(MYDIR, 'koalified'))]
    cmdclass['build_ext'] = build_ext


class PyTest(TestCommand):
    extra_kwargs = {'tests_require': ['pytest', 'mock']}

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        sys.exit(pytest.main(self.test_args))


cmdclass['test'] = PyTest

try:
   import pypandoc
   readme = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError, OSError, RuntimeError):
   readme = ''

setup(name='koalified',
      version='0.0.2',
      description='For when truth is a little fuzzy.',
      long_description=readme,
      author='DomainTools',
      author_email='timothy@domaintools.com',
      url='https://github.com/domaintools/koalified_python',
      license="MIT",
      # entry_points={
      #  'console_scripts': [
      #      'koalified = koalified:run.terminal',
      #  ]
      #},
      packages=['koalified'],
      requires=[],
      install_requires=['PyYAML', 'validators', 'requests', 'xxhash', 'phonenumbers', 'pycountry', 'arrow'],
      cmdclass=cmdclass,
      ext_modules=ext_modules,
      keywords='Python, Python3',
      classifiers=['Development Status :: 6 - Mature',
                   'Intended Audience :: Developers',
                   'Natural Language :: English',
                   'Environment :: Console',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Utilities'],
      **PyTest.extra_kwargs)
