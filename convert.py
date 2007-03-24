#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""Dictionary cleanup tool.

This module assists into the conversion of a ISpell/MySpell dictionary for the
use as full-text search dictionary in PostgreSQL using the tsearch2 tool.
"""

# Copyright (C) 2007 by Daniele Varrazzo
# $Id$
__version__ = "$Revision$"[11:-2]

import locale

def getRevision(filename):
    from subprocess import Popen, PIPE
    import cElementTree as et

    f = Popen(['svn', 'info', filename, '--xml'], stdout=PIPE).stdout
    tree = et.parse(f)
    return int(tree.find('entry').get('revision'))
    

class Dictionary(dict):
    """A language dictionary.

    A dictionary is implemented as... a `dict`. The keys are the words,
    the values are the flags if any, else `None`.
    """
    header = None
    """The dictionary comment, on the file head."""

    def load(self, filename):
        self.clear()
        h = []
        for row in open(filename):
            if row.startswith('/'):
                h.append(row)
                continue

            row = row.rstrip()
            if row == '':
                continue

            p = row.rstrip().split('/')
            if len(p) == 1:
                self[p[0]] = None
            else:
                self[p[0]] = p[1]

        self.header = ''.join(h)

    def save(self, filename):
        f = file(filename, 'w')
        f.write(self.header)

        ws = list(self.iterkeys())
        # Sort in correct order... but the original file is sorted in ASCII
        #ws.sort(cmp=lambda a,b: locale.strcoll(a.lower(), b.lower()))

        #for w in ws:
            #f.write(w)
            #flags = self[w]
            #if flags is not None:
                #f.write("/")
                #f.write(flags)
            #f.write('\n')

        o = []
        for w, fl in self.iteritems():
            if not fl:
                o.append(w)
            else:
                o.append("%s/%s" % (w,fl))

        o.sort()
        f.write("\n".join(o))
        f.write('\n')

class Operation(object):
    """An operation to perform on a dictionary.
    """

    label = "Basic operation. To be subclassed."
    """A textual representation of the operation."""

    def __init__(self, label=None):
        if label is not None: self.label = label
        
    def run(self, dictionary):
        print self.label
        return self._run(dictionary)
    
    def _run(self, dictionary):
        raise NotImplementedError


class RemoveWords(Operation):
    """Remove all the words from a dictionary matching a predicate."""
    def __init__(self, predicate, **kwargs):
        super(RemoveWords, self).__init__(**kwargs)
        self.predicate = predicate

    def _run(self, dictionary):
        to_del = filter(self.predicate, dictionary)
        for k in to_del:
            del dictionary[k]

class DropFlag(Operation):
    """Remove a flag from all the words."""
    def __init__(self, flag, **kwargs):
        super(DropFlag, self).__init__(**kwargs)
        self.flag = flag

    def _run(self, dictionary):
        flag = self.flag
        for w,f in dictionary.iteritems():
            if f and flag in f:
                dictionary[w] = "".join(f.split(flag))

#: The list of operation to perform.
#: The first item is the revision number after which the operation is not to
#: be performed. Other parameters are the callable to run and the positional
#: and 
processes = [
    (13, RemoveWords(label="Togli le parole contenenti un apostrofo.",
        predicate=lambda w: "'" in w)),
    (16, DropFlag(label="Rimuovi il flag T (prefisso accentato).",
        flag="T")),
    (16, DropFlag(label="Rimuovi il flag U (un, ciascun).",
        flag="U")),
    (16, DropFlag(label="Rimuovi il flag X (pronomi tronchi).",
        flag="X")),
    (16, DropFlag(label="Rimuovi il flag i (articolo L').",
        flag="i")),
    (16, DropFlag(label="Rimuovi il flag q (prefisso bell').",
        flag="q")),
    (16, DropFlag(label="Rimuovi il flag r (prefisso brav').",
        flag="r")),
    (16, DropFlag(label="Rimuovi il flag s (prefisso buon').",
        flag="s")),
    (16, DropFlag(label="Rimuovi il flag ^ (prefisso sant').",
        flag="^")),
]

if __name__ == '__main__':
    d_name = 'italian.dict'
    locale.setlocale(locale.LC_ALL, 'it_IT')
    
    d_rev = getRevision(d_name)

    dct = Dictionary()
    print "loading"
    dct.load(d_name)
    
    for p_rev, proc in processes:
        if p_rev >= d_rev:
            proc.run(dct)

    print "saving"
    dct.save(d_name)
