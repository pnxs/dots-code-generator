#!/usr/bin/env python

from distutils.core import setup

setup(name='dots',
      version='1.0',
      requires=["jinja2", "SimpleParse", 'cbor'],
      packages=['dots'])