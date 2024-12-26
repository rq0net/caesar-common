#!/usr/bin/env python

import os
from setuptools import setup, find_packages

__version__ = "1.0.0"

here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, 'README.md')) as f:
    long_description = f.read().strip()

setup(
    name='caesar-common',
    version=__version__,
    author='rq0net',
    author_email='rq0net@gmail.com',
    url='https://github.com/rq0net/caesar-common',
    license='Apache License 2.0',
    description='''
    Auth Public.
    Read the README.md for more information.
    ''',
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/x-rst',
    keywords='''
    django rest auth registration rest-framework django-registration api docker cookiecuter tox pytest
    ''',
    zip_safe=False,
    include_package_data=True,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, >=3.8",
    # https://pypi.org/classifiers/
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet :: WWW/HTTP'
    ],
)
