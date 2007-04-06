#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""Dictionary cleanup tool.

This module assists into the conversion of a ISpell/MySpell dictionary for the
use as full-text search dictionary in PostgreSQL using the tsearch2 tool.
"""

# Copyright (C) 2007 by Daniele Varrazzo
# $Id$
__version__ = "$Revision$"[11:-2]

import re
import locale
from operator import itemgetter

import psycopg2

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
                self[p[0]] = ''
            else:
                self[p[0]] = p[1]

        self.header = ''.join(h)

    def save(self, filename):
        f = file(filename, 'w')
        if self.header:
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

    def update(self, other):
        """Add a dictionary to this dictionary.

        Add new words, merge existing flags.
        """
        for w, f in other.iteritems():
            if w not in self:
                self[w] = f
                continue

            if f:
                self[w] = ''.join(sorted(set((self[w] or '') + f)))

class Operation(object):
    """An operation to perform on a dictionary.
    """

    label = "Basic operation. To be subclassed."
    """A textual representation of the operation."""

    def __init__(self, label=None):
        self.label = label or self.__class__.__name__
        
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

class RenameFlag(Operation):
    """Change a flag letter."""
    def __init__(self, flag_in, flag_out, **kwargs):
        super(RenameFlag, self).__init__(**kwargs)
        self.flag_in = flag_in
        self.flag_out = flag_out

    def _run(self, dictionary):
        flag_in = self.flag_in
        flag_out = self.flag_out
        for w,f in dictionary.iteritems():
            if f and flag_in in f:
                dictionary[w] = flag_out.join(f.split(flag_in))

class PassatoRemotoIrregolare(Operation):
    eccezioni = set([
        'assurgere', 'capovolgere', 'convergere', 'dirigere', 'divergere',
        'eleggere', 'erigere', 'esigere', 'frangere', 'fungere', 'indulgere',
        'prediligere', 'recingere', 'redigere', 'redirigere', 'ricingere',
        'ridirigere', 'rifrangere', 'sorreggere', 'succingere', 'transigere',
        'urgere'])

    def __init__(self, flag, **kwargs):
        super(PassatoRemotoIrregolare, self).__init__(**kwargs)
        self.flag = flag

    def _run(self, dictionary):
        for w,f in list(dictionary.iteritems()):
            if not f or 'B' not in f:
                continue

            if w.endswith("ggere") and w not in self.eccezioni:
                dictionary[w] = (dictionary[w] or '') + self.flag
                tema = w[:-5]
                for suf in ('ssi', 'sse', 'ssero'):
                    dictionary.pop(tema+suf, None)

            elif w.endswith("gere") and w not in self.eccezioni:
                dictionary[w] = (dictionary[w] or '') + self.flag
                tema = w[:-4]
                for suf in ('si', 'se', 'sero'):
                    dictionary.pop(tema+suf, None)

class RimuoviFemminileInPp(Operation):
    def _run(self, dictionary):
        for w,f in list(dictionary.iteritems()):
            if w.endswith('a') and f and 'Q' in f \
            and 'F' in (dictionary.get(w[:-1]+'o') or ''):
                del dictionary[w]

class UnisciAggettiviMaschileFemminile(Operation):
    """Unisci aggettivi presenti in doppia forma."""
    def _run(self, dictionary):
        keep = RimuoviVerbi.keep
        for w, f in list(dictionary.iteritems()):
            if not f or 'O' not in f:
                continue

            fw = w[:-1] + 'a'
            if 'Q' in (dictionary.get(fw) or ''):
                if w in keep['O'] or fw in keep['Q']: continue

                del dictionary[fw]
                dictionary[w] = f.replace('O', 'o')

class RimuoviFemminileParticipioPassato(Operation):
    """Non serve: si ottiene per produzione."""
    def _run(self, dictionary):
        keep = RimuoviVerbi.keep
        for w, f in list(dictionary.iteritems()):
            if not f or 'm' not in f:
                continue

            fw = w[:-1] + 'a'
            if 'Q' in (dictionary.get(fw) or ''):
                if fw in keep['Q']: continue

                del dictionary[fw]

class UnisciAggettivoInCio(Operation):
    """Non serve: si ottiene per produzione. Richiede modifica di /o"""
    def _run(self, dictionary):
        keep = RimuoviVerbi.keep
        for w, f in list(dictionary.iteritems()):
            if not f or 'n' not in f or not w.endswith('a'):
                continue

            mw = w[:-1] + 'o'
            mf = dictionary.get(mw) or ''
            if 'O' in mf:
                if mw in keep['O']: continue

                del dictionary[w]
                dictionary[mw] = mf.replace('O', 'o')

class UnisciMestieri(Operation):
    """Femminile in ..trice unito al maschile in ..tore"""
    def _run(self, dictionary):
        keep = RimuoviVerbi.keep
        for w, f in list(dictionary.iteritems()):
            if not f or 'S' not in f or not w.endswith('tore'):
                continue

            fw = w[:-3] + 'rice'
            if fw not in dictionary: continue
            mf = dictionary[fw] or ''
            assert mf == 'S', w
            if 'S' in mf:
                del dictionary[fw]
                dictionary[w] = f + 'f'

class EliminaQuErre(Operation):
    """La combinazione /Q /R è usata a volte al posto di /u sul maschile."""
    def _run(self, dictionary):
        keep = RimuoviVerbi.keep
        for w, f in list(dictionary.iteritems()):
            if not f or 'Q' not in f or 'R' not in f:
                continue
            mw = w[:-1] + 'o'
            if mw not in dictionary:
                continue

            mf = dictionary[mw] or ""
            assert f in ('QR', 'RQ'), w

            del dictionary[w]

            fnew = 'p'
            if fnew not in mf:
                dictionary[mw] = mf + fnew
            else:
                print mw

class UnisciParoleConiugazioni(Operation):
    def _run(self, dictionary):
        keep = Dictionary(); keep.load("non-verbi.dict")
        dictionary.update(keep)

        # Ora pensiamo ai plurali in e, che tipicamente sono a parte perché
        # spesso non corrisponde a nessuna coniugazione.
        for w, f in keep.iteritems():
            if not f: continue

            print w,
            if 'Q' in f:
                if w[-2] in 'cg':
                    pl = w[:-1] + 'he'
                else:
                    pl = w[:-1] + 'e'

            elif 'o' in f:
                #[^GCI]O    > -O,E
                #[^GC]IO    > -O,E
                #[GC]IO    > -IO,E
                #[GC]O    > -O,HE
                if w[-2] not in ('cgi'):
                    pl = w[:-1] + 'e'
                elif w[-2] == 'i' and w[-3] not in ('cg'):
                    pl = w[:-1] + 'e'
                elif w[-2] == 'i':
                    pl = w[:-2] + 'e'
                else:
                    pl = w[:-1] + 'he'

            elif 'p' in f:
                if w[-2] in 'cg':
                    pl = w[:-1] + 'he'
                else:
                    pl = w[:-1] + 'e'

            elif 'n' in f:
                pl = w[:-2] + 'e'

            elif 'O' in f or 'S' in f or 'N' in f:
                continue

            else:
                assert False, "%s/%s" % (w, f)

            print pl

            if pl not in dictionary:
                continue

            if pl in ('sole','molle'): continue
            
            pf = dictionary[pl]
            assert not pf or 'B' in pf, "%s/%s" % (pl, pf)
            del dictionary[pl]

class UnisciIoIi(Operation):
    def _run(self, dictionary):
        for w, f in list(dictionary.iteritems()):
            if not w.endswith('io'): continue
            pl = w[:-2] + 'ii'
            if not pl in dictionary: continue

            assert not dictionary[pl]
            dictionary[w] = (f or '') + 'n'
            del dictionary[pl]

class RimuoviVerbi(Operation):
    """Rimuovi i verbi dal vocabolario!!!
    """
    # Eccezioni: da non rimuovere anche se appaiono coniugazioni. La chiave
    # è il flag che le 'tiene in vita'.
    keep = {
        # rimosso: usare il dizionario ``non-verbi.dict`` per questo compito.
    }

    def _run(self, dictionary):
        vflags = set('ABCztjÀPVZ')  # flag che indicano verbi
        aflags = set('IvsagDEFGHmb')  # attributi che vanno solo sui verbi
        pflags = set('Jde')  # flag che indicano prefissi
        kflags = set('WY')  # flag che vanno su aggettivi, ecc, quindi
                            # sono da mantenere

        cnn = psycopg2.connect(database='tstest')
        cur = cnn.cursor()
        cur.execute(
            "SELECT coniugazione"
            " FROM coniugazione JOIN attributo_mydict USING (infinito)"
            " WHERE attributo = 'presente'"
            ";")

        cons = set(map(itemgetter(0), cur))
        cur.close()
        cnn.close()

        dflags = vflags | aflags | pflags | kflags
        for w, f in list(dictionary.iteritems()):
            if w not in cons:
                continue
            f = (f and set(f) or set()) - dflags
            
            if not f:
                if w not in self.keep[None]:
                    del dictionary[w]
            else:
                for l in f:
                    if w in self.keep[l]:
                        dictionary[w] = ''.join(f)
                        break
                else:
                    del dictionary[w]
                
class UnisciMestieri2(Operation):
    """Femminile in ..trice unito al maschile in ..tore

    Su molti mestrieri maschili manca la 'S': questa operazione corregge anche
    quelli.
    """
    def _run(self, dictionary):
        keep = RimuoviVerbi.keep
        for w, f in list(dictionary.iteritems()):
            if not w.endswith('tore'):
                continue

            fw = w[:-3] + 'rice'
            if fw not in dictionary: continue
            ff = dictionary[fw] or ''
            assert ff == 'S', w

            f = f or ''
            if 'S' not in f:
                f += 'S'

            del dictionary[fw]
            dictionary[w] = f + 'f'

class UnisciAvverbi(Operation):
    def _run(self, dictionary):
        already_flagged = 0
        for w, f in list(dictionary.iteritems()):
            if w.endswith('amente'):
                flag = 'Y'
                aggs = [w[:-6] + 'o', w[:-5] + 'o']
            elif w.endswith('emente') or w.endswith('lmente'):
                flag = w.endswith("e") and 'Y' or 'y'
                aggs = [w[:-6] + 'o', w[:-5] + 'o', w[:-5] + 'e', w[:-5]]
            else:
                continue

            for agg in aggs:
                if agg in dictionary and agg[-1] in 'aeiou':
                    print agg, "->", w
                    if flag not in (dictionary[agg] or ''):
                        dictionary[agg] = (dictionary[agg] or '') + flag
                    else:
                        already_flagged += 1
                    del dictionary[w]
                    break

        print "already_flagged", already_flagged

class UnisciPlurali(Operation):
    """Unisci il plurale al suo singolare."""
    def _run(self, dictionary):
        for w, f in list(dictionary.iteritems()):
            if w.endswith('o'):
                flag = 'O'
                pll = [ w[:-1] + 'i', w[:-1] + 'hi']
            elif w.endswith('e'):
                flag = 'S'
                pll = [ w[:-1] + 'i', w[:-1] + 'hi']
            elif w.endswith('a'):
                flag = 'Q'
                pll = [ w[:-1] + 'e', w[:-1] + 'he']
            else:
                continue

            # può essere stato già rimosso
            if w not in dictionary:
                continue

            for pl in pll:
                if pl in dictionary:
                    print pl, '->', w
                    del dictionary[pl]
                    if flag not in f:
                        dictionary[w] += flag
                    break

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
    (17, RenameFlag(label="Unisci i flag D ed E (pronominali, riflessivi)",
        flag_in="E", flag_out="D")),
    (22, PassatoRemotoIrregolare(label="Aggiungi flag per p.r. 2a coniugazione"
                                       " (sconfiggere -> sconfissi)",
        flag='s')),
    (24, RimuoviFemminileInPp(label="Rimuovi sostantivi femminili se c'è un"
                                    "participio passato che li include.")),
    (33, RimuoviFemminileParticipioPassato()),
    (33, UnisciAggettiviMaschileFemminile()),
    (34, UnisciAggettivoInCio()),
#    (xx, RimuoviVerbi(label="Togli tutti i verbi!!!",)),
    (37, UnisciMestieri()),
    (39, EliminaQuErre()),
    (45, UnisciParoleConiugazioni()),
    (46, UnisciIoIi()),
    (47, UnisciMestieri2()),
    (49, UnisciAvverbi()),
    (50, UnisciPlurali()),
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
