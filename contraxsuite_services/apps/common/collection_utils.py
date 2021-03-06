"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""
# -*- coding: utf-8 -*-

from typing import Iterable, List, Sequence

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def sequence_chunks(col: Sequence, n: int) -> Iterable[List]:
    """
    Split sequence to chunks of length n. Suitable for lists, django query sets (will execute separate
    sql query per chunk).
    :param col:
    :param n:
    :return:
    """
    i = 0
    while True:
        block = col[i:i + n]
        if block:
            if not isinstance(block, list):
                block = list(block)
            yield block
            i = i + n
        else:
            break


def iterable_chunks(col: Iterable, n: int) -> Iterable[List]:
    """
    Split iterable to chunks of length n by iterating it and buffering. Suitable for generators, probably for reading
    files line by line.
    :param col:
    :param n:
    :return:
    """
    block = list()
    for elem in col:
        block.append(elem)
        if len(block) == n:
            yield block
            block = list()
    if block:
        yield block


def chunks(col: Iterable, n: int) -> Iterable[List]:
    """
    Split iterable to chunks of length n using the best suitable splitting method - slicing for the types
    supporting it (lists, query sets, e.t.c.) or
    iterating with buffering for other types (generators, sets).
    :param col:
    :param n:
    :return:
    """
    if col is None:
        return

    if hasattr(col, '__getitem__'):
        # noinspection PyTypeChecker
        yield from sequence_chunks(col, n)
    else:
        yield from iterable_chunks(col, n)
