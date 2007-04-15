#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""Dividi in 3 parti il dizionario di italiano.
"""

# Copyright (C) 2007 by Daniele Varrazzo
# $Id$
__version__ = "$Revision$"[11:-2]

import string

from convert import Dictionary

din = Dictionary()
din.load("italian.dict")

dv = Dictionary(); dv.header = din.header
dn = Dictionary(); dn.header = din.header
dx = Dictionary(); dx.header = din.header

dicts = {}
for _ in string.uppercase + string.digits:
    dicts[_] = dv
for _ in string.lowercase:
    dicts[_] = dx

for w, f in din.iteritems():
    if not f:
        dx[w] = f
        continue

    for flag in f:
        do = dicts.get(flag, dn)
        do[w] = do.get(w, '') + flag

dv.save('italian-verbs.dict')
dn.save('italian-numbers.dict')
dx.save('italian-other.dict')
