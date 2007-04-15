#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""Merge many dictionaries into a single dictionary.
"""

# Copyright (C) 2007 by Daniele Varrazzo
# $Id$
__version__ = "$Revision$"[11:-2]

import sys

from convert import Dictionary

in_dicts = []
for fn in sys.argv[1:]:
    d = Dictionary()
    d.load(fn)
    in_dicts.append(d)

do = Dictionary()

for di in in_dicts:
    if not do.header and di.header:
        do.header = di.header
    for w, f in di.iteritems():
        do[w] = do.get(w, '') + f

do.save(sys.stdout)
