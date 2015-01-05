#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
    from setuptools import find_packages
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='note',
    version='0.5.1',
    description='A command line based note taking application',
    long_description=readme + '\n\n' + history,
    author='Devin Kelly',
    author_email='dwwkelly@fastmail.fm',
    url='https://github.com/dwwkelly/note',
    packages=find_packages(exclude=['tests']),
    scripts=['scripts/noted', 'scripts/notec', 'scripts/server'],
    package_dir={'note': 'note'},
    include_package_data=True,
    license="GPL3",
    zip_safe=False,
    keywords='note',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
    install_requires=['pymongo', 'tornado', 'pyzmq>=14.3.1',
                      'markdown', 'flask', 'mock', 'dateparser',
                      'click', 'python-daemon', 'lockfile'],
    test_suite="tests"
)
