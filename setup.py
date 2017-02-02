# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='clicol',
    version='0.0.1',
    description='CLI colorizer',
    long_description=readme,
    author='Viktor Kertesz',
    author_email='vkertesz2@gmail.com',
    url='https://github.com/realvitya/clicol',
    license=license,
    packages=find_packages(exclude=('tests'))
)
