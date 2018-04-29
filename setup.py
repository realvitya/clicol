# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

PACKAGE = "clicol"
NAME = "clicol"
DESCRIPTION = "CLI colorizer"
AUTHOR = "Viktor Kertesz"
AUTHOR_EMAIL = "vkertesz2@gmail.com"
URL = "https://github.com/realvitya/clicol"
VERSION = __import__(PACKAGE).__version__
LONGDESCRIPTION=open("README.rst", "rt").read()

setup(
    name='clicol',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONGDESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license="GPLv3",
    packages=find_packages(exclude=('tests')),
    package_data={'clicol': ['ini/*.ini']},

    data_files=[
        ('share/doc/clicol', ['doc/bashrc','doc/clicol.cfg']),
    ],
    install_requires=[
        'pexpect',
    ],
    entry_points={
            'console_scripts': [
                    'clicol-telnet = clicol.clicol:main',
                    'clicol-ssh    = clicol.clicol:main',
                    'clicol-test   = clicol.clicol:main',
                    'clicol-file   = clicol.clicol:main',
                    'clicol-cmd    = clicol.clicol:main',
                ],
        },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.7",
    ],
    zip_safe=False,
)
