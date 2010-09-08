#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Copyright 2010 Espen Rønnevik <brightside@quasinet.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup

CLASSIFIERS = filter(None, map(str.strip,
"""
Intended Audience :: Developers
Development Status :: 3 - Alpha
Programming Language :: Python :: 3
Operating System :: POSIX
Topic :: Communications
Topic :: Internet
Topic :: System :: Networking
Topic :: Software Development :: Libraries :: Python Modules
License :: OSI Approved :: GNU General Public License (GPL)
""".splitlines()))

setup(name='esocket',
    version='0.1.0',
    description='an asynchronous eventsocket library using pyev',
    author='Espen Rønnevik',
    author_email='brightside@quasinet.org',
    url='http://github-blabla',
    packages=['esocket'],
    classifiers=CLASSIFIERS)
