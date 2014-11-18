#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
    from setuptools import find_packages
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='note',
    version='0.2',
    description='A command line based not taking application',
    long_description=readme + '\n\n' + history,
    author='Devin Kelly',
    author_email='dwwkelly@fastmail.fm',
    url='https://github.com/dwwkelly/note',
    packages=find_packages(),
    scripts=['scripts/noted', 'scripts/notec', 'scripts/server'],
    package_dir={'note': 'note'},
    include_package_data=True,
    license="GPL3",
    zip_safe=False,
    keywords='note',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPL3 License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
    test_suite='tests',
    tests_require=[],
    install_requires=['pymongo', 'tornado', 'pyzmq']
)
