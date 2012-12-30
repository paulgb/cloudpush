#!/usr/bin/env python

from setuptools import setup

setup(name='cloudpush',
    version='0.2',
    description='One-way file synchronization tool for Rackspace Cloud Files and other OpenStack Swift services',
    author='Paul Butler',
    author_email='paulgb@gmail.com',
    url='https://github.com/paulgb/cloudpush',
    packages=['cloudpush'],
    scripts=['cloudpush/cloudpush.py'],
    install_requires=[
      'python-cloudfiles >= 1.7.10'
    ]
)

