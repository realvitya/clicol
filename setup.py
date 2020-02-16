# -*- coding: utf-8 -*-

""" CLICOL - Colorize CLI and more

    Copyright (C) 2017-2019 Viktor Kertesz
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    If you need to contact the author, you can do so by emailing:
    vkertesz2 [~at~] gmail [/dot\] com
"""

from setuptools import setup, find_packages

PACKAGE = "clicol"
NAME = "clicol"
DESCRIPTION = "CLI colorizer"
AUTHOR = "Viktor Kertesz"
AUTHOR_EMAIL = "vkertesz2@gmail.com"
URL = "https://github.com/realvitya/clicol"
VERSION = __import__(PACKAGE).__version__
LONGDESCRIPTION=open("README.md").read()

setup(
    name='clicol',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONGDESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license="GPLv3",
    packages=find_packages(exclude='tests'),
    package_data={'clicol': ['ini/*.ini']},

    data_files=[
        ('share/doc/clicol', ['doc/bashrc','doc/clicol.cfg']),
    ],
    install_requires=[
        'pexpect',
    ],
    extras_require={
        ':python_version < "3"': [
            'future',
        ],
    },
    entry_points={
            'console_scripts': [
                    'clicol-telnet = clicol.clicol:main',
                    'clicol-ssh    = clicol.clicol:main',
                    'clicol-test   = clicol.clicol:main',
                    'clicol-file   = clicol.clicol:main',
                    'clicol-cmd    = clicol.clicol:main',
                ],
            'clicol.plugins': [
                    'HumanNumbers = clicol.builtinplugins.humannumbers:HumanNumbers',
                ],
        },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
    zip_safe=False,
)
