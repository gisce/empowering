#!/usr/bin/env python
"""
Empowering
======

Python library for the Empowering REST API.

:copyright: (c) 2013 by GISCE-TI, S.L., see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""
from setuptools import setup, find_packages

tests_require = [
    'Flask'
]

install_requires = [
    'libsaas',
    'marshmallow'
]

setup(
    name='empowering',
    version='0.13.1',
    author='GISCE-TI, S.L.',
    author_email='devel@gisce.net',
    url='http://code.gisce.net/empowering',
    description='Python library for the Empowering REST API.',
    long_description=__doc__,
    license='MIT',
    packages=find_packages(exclude=['tests', 'test']),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='nose.collector',
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
