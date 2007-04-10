#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""Classificazione delle coniugazioni.

Classifica i verbi in base alla loro coniugazione:

Dato un infinito, prendi tutte le sue forme, ovvero:

- 6 indicativo presente
- 6 indicativo imperfetto
- 6 indicativo passato
- 6 indicativo futuro
- 6 congiuntivo presente
- 6 congiuntivo imperfetto
- 6 condizionale
- 5 imperativo
- 1 gerundio
- 1 participio presente
- 1 participio passato

Calcola la produzione necessaria dall'infinito, ovvero il prefisso da togliere
e quello da aggiungere per ottenere ogni forma.
"""

# Copyright (C) 2007 by Daniele Varrazzo
# $Id$
__version__ = "$Revision$"[11:-2]

import sys
from operator import itemgetter
from itertools import cycle

import psycopg2

import affix
from calcflag import calcFlags, toFlags

def main():
    import string; fls = list(string.uppercase + string.digits)
    import espansioni

    infs = dbRun(getInfiniti)
    flags = []

    for var in ('t', 'p', 'r', 'rp'):
        flag = affix.Flag(fls.pop(0))
        flag.comment = getLabel('inf', variazione=var)
        flags.append(flag)
        for mtp in ('inf1', 'inf2'):
            exp = getattr(espansioni, "%s_%s" % (mtp, var))
            flag.productions.extend(exp)

    forms = dbRun(getForms1, infs)
    fdata = calcFlags(forms)
    flags1 = toFlags(fdata, fls, forms)
    flags.extend(flags1)

    mps = [(m, p) for m in range(1,9) for p in range(6) if (m, p) != (8,0)]
    for flag in flags1:
        flag.comment = "indicativo, congiuntivo, condizionale, imperativo"
        prev = None
        for prod in flag.productions:
            if prod.pattern != prev:
                prev = prod.pattern
                i = 0
            prod.line_comment = getLabel(modotempo=mps[i][0], persona=mps[i][1])
            i += 1

    forms = dbRun(getForms3, infs)
    fdata = calcFlags(forms)
    flags1 = toFlags(fdata, fls[:], forms)

    for var in ('p', 'r', 'rp'):
        for flag_o in flags1:
            flag = affix.Flag(fls.pop(0))
            flag.comment = getLabel("imperativo", variazione=var)

            flags.append(flag)
            assert len(flag_o.productions) % 5 == 0
            for i in range(0, len(flag_o.productions), 5):
                for prod, mtp in zip(flag_o.productions[i:i+5],
                    cycle(('imp2s','imp3s','imp1p','imp2p','imp3p'))):
                    exp = getattr(espansioni, "%s_%s" % (mtp, var), None)
                    if not exp or isinstance(prod, affix.Difettivo):
                        flag.productions.append(prod)
                    else:
                        flag.productions.extend(prod + p2 for p2 in exp)
                        flag.productions[-len(exp)].comment = (
                            prod.comment and prod.comment.replace(
                                "*" + flag_o.letter, "*" + flag.letter))

    forms = dbRun(getForms2, infs)
    fdata = calcFlags(forms)
    flags1 = toFlags(fdata, fls[:], forms)

    for var in ('n', 'p', 'r', 'rp'):
        for flag_o in flags1:
            flag = affix.Flag(fls.pop(0))
            flag.comment = getLabel("participio, gerundio",
                variazione=var)

            flags.append(flag)
            assert len(flag_o.productions) % 3 == 0
            for i in range(0, len(flag_o.productions), 3):
                for prod, mtp in zip(flag_o.productions[i:i+3],
                    cycle(('ppr','ppa','ger'))):
                    exp = getattr(espansioni, "%s_%s" % (mtp, var), None)
                    if not exp or isinstance(prod, affix.Difettivo):
                        flag.productions.append(prod)
                    else:
                        flag.productions.extend(prod + p2 for p2 in exp)
                        flag.productions[-len(exp)].comment = (
                            prod.comment and prod.comment.replace(
                                "*" + flag_o.letter, "*" + flag.letter))

    # Stampa
    # ------

    print "\n\n".join(map(str, flags))

    def suffKey(s):
        if ']' in s:
            s1, s2 = s.split(']',1)
            s = s1[1] + s2

        return ''.join(reversed(s))

    for i, flag in enumerate(fdata):
        print >>sys.stderr, "\nflag", i
        for k, v in sorted(flag.iteritems(),key=lambda _: suffKey(_[1])):
            print >>sys.stderr, "   ", v, ":", k
            print >>sys.stderr, "              #", len(forms[k]), forms[k][:3]

# Risultati: sono necessari

# - 4 flag per tutti gli indicativi, congiuntivi, condizionali

# - 4 flag per tutti gli imperativi
# - 4 flag per tutti i participi e gerundi
# - 5 flag per tutti gli imperativi, participi e gerundi insieme.

# - 5 flag per tutto!

# Quello che farei:
# - 4 flag per tutti gli indicativi, congiuntivi, condizionali
# - 5 flag per tutti gli imperativi, participi e gerundi insieme.
# - 5 flag per aggiungere particelle riflessive.
# - 5 flag per aggiungere particelle pronominali.
# - 5 flag per aggiungere la combinazione di entrambe.

# n.b. in un flag dei participi c'è solo udire, quindi le 4 forme
# potrebbero essere messe insieme. Bastano 21 flag per rappresentare
# tutti i verbi con la corretta selezione delle forme pronominali e riflessive.

def dbRun(f, *args, **kwargs):
    cnn = psycopg2.connect(database='tstest')
    try:
        cur = cnn.cursor()
        try:
            return f(cur, *args, **kwargs)
        finally:
            cur.close()
    finally:
        cnn.close()

def getInfiniti(cur):
    cur.execute("SELECT DISTINCT infinito FROM coniugazione"
    #    " INNER JOIN attributo_vrbl USING (infinito) WHERE attributo = 'presente'"
        ";")

    return map(itemgetter(0), cur)

def calcProd(inf, term):
    for i in xrange(len(inf),-1,-1):
        if term.startswith(inf[:i]):
            return inf[i:], term[i:]

def getForms1(cur, infs):

    forms = {}
    for inf in infs:
        print >>sys.stderr, inf

        # Lista in ordine fisso
        cur.execute("SELECT coniugazione FROM coniugazione"
                    " WHERE infinito = %s"
                    " AND modotempo <= 8"
                    " ORDER BY modotempo, persona;", (inf,))

        cons = map(itemgetter(0), cur)
        if not cons: continue
        prod = tuple(calcProd(inf, _) for _ in cons)

        forms.setdefault(prod, []).append(inf)

    return forms

def getForms3(cur, infs):

    forms = {}
    for inf in infs:
        print >>sys.stderr, inf

        # Lista in ordine fisso
        cur.execute("SELECT coniugazione FROM coniugazione"
                    " WHERE infinito = %s"
                    " AND modotempo = 8"
                    " ORDER BY modotempo, persona;", (inf,))

        cons = map(itemgetter(0), cur)
        if not cons: continue
        prod = tuple(calcProd(inf, _) for _ in cons)

        forms.setdefault(prod, []).append(inf)

    return forms

def getForms2(cur, infs):
    forms = {}
    for inf in infs:
        print >>sys.stderr, inf

        ## Lista in ordine fisso
        cur.execute("SELECT modotempo, persona, coniugazione "
                    " FROM coniugazione"
                    " WHERE infinito = %s"
                    " AND modotempo > 8"
                    " ORDER BY modotempo, persona;", (inf,))

        cons = dict(((t[0],t[1]),t[2]) for t in cur)
        if not cons: continue

        prod = tuple(k in cons and calcProd(inf, cons[k]) or None
            for k in [(9,0),(10,0),(11,0)])

        # Lista minimale
        #cur.execute("SELECT coniugazione FROM coniugazione"
                    #" WHERE infinito = %s"
                    #" AND modotempo >= 8"
                    #" ORDER BY modotempo, persona;", (inf,))

        #cons = map(itemgetter(0), cur)
        #if not cons: continue
        #prod = tuple(calcProd(inf, _) for _ in cons)

        forms.setdefault(prod, []).append(inf)

    return forms

lbl_variazione = {
    'n': None,
    't': "troncamento",
    'p': "particelle pronominali",
    'r': "forma riflessiva",
    'rp': "particelle pronominali su forma riflessiva",
}

lbl_modotempo = {
    1:  "ind.  pres.",
    2:  "ind.  imp. ",
    3:  "ind.  pass.",
    4:  "ind.  fut. ",
    5:  "cong. pres.",
    6:  "cong. pass.",
    7:  "cond.",
    8:  "imp.",
    9:  "part. pres.",
    10: "part. pass.",
    11: "ger.",
}

lbl_persona = {
    0: "1a p. sn.",
    1: "2a p. sn.",
    2: "3a p. sn.",
    3: "1a p. pl.",
    4: "2a p. pl.",
    5: "3a p. pl.",
}

def getLabel(modotempo=None, persona=None, variazione=None):
    if isinstance(modotempo, basestring) or modotempo > 8:
        o = lbl_modotempo.get(modotempo, modotempo)
    else:
        o = "%s %s" % (lbl_modotempo[modotempo], lbl_persona[persona])

    if lbl_variazione.get(variazione):
        o = "%s su %s" % (lbl_variazione[variazione], o)

    return o

lbl_modotempo['imp2s'] = getLabel(modotempo=8,  persona=1)
lbl_modotempo['imp3s'] = getLabel(modotempo=8,  persona=2)
lbl_modotempo['imp1p'] = getLabel(modotempo=8,  persona=3)
lbl_modotempo['imp2p'] = getLabel(modotempo=8,  persona=4)
lbl_modotempo['imp3p'] = getLabel(modotempo=8,  persona=5)
lbl_modotempo['ppr']   = getLabel(modotempo=9,  persona=0)
lbl_modotempo['ppa']   = getLabel(modotempo=10, persona=0)
lbl_modotempo['ger']   = getLabel(modotempo=11, persona=0)
lbl_modotempo['inf']   = getLabel("infinito")
lbl_modotempo['inf1']  = getLabel("infinito")
lbl_modotempo['inf2']  = getLabel("infinito")

if __name__ == '__main__':
    main()
