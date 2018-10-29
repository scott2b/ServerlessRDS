#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='slsrds',
      version='0.0.1',
      description='Serverless management of RDS databases',
      author='Scott B. Bradley',
      packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
      license='MIT',
    )
