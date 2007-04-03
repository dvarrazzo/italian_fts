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

class RimuoviVerbi(Operation):
    """Rimuovi i verbi dal vocabolario!!!
    """
    # Eccezioni: da non rimuovere anche se appaiono coniugazioni. La chiave
    # è il flag che le 'tiene in vita'.
    keep = {
        'N': ['stufa', 'pipa', 'anima', 'visita', 'idea', 'domanda', 'cucina',
            'tonda'],
        'O': ['abbacchio', 'abbaglio', 'abbaino', 'abbandono', 'abbozzo',
            'abbraccio', 'abbuono', 'abitino', 'abito', 'abortivo', 'abuso',
            'accento', 'acchito', 'acciacco', 'acciaino', 'acciaio', 'acconcio',
            'accordo', 'accumulo', 'aceto', 'acidulo', 'acquarello', 'acquerello',
            'acquisito', 'acquisto', 'adagio', 'adatto', 'addebito', 'addobbo',
            'adito', 'adultero', 'aerotraino', 'alberghino', 'arreso',
            'assassino', 'bacino', 'baracchino', 'becchino', 'bilancino',
            'biscottino', 'bordo', 'brando', 'buchino', 'calcio', 'cappottino',
            'carato', 'cardano', 'carrozzino', 'codicillo', 'compatto',
            'compitino', 'concorso', 'contentino', 'contratto', 'corredino',
            'cortocircuito', 'cricco', 'cucinino', 'discorso', 'disegnino',
            'disormeggio', 'divano', 'divello', 'esatto', 'esperimento',
            'esplicito', 'estivo', 'fato', 'fatto', 'forno', 'fotografo',
            'gommino', 'grugno', 'imbrago', 'imbuto', 'impietoso', 'incolto',
            'indulto', 'infisso', 'infuso', 'intervallo', 'letto', 'listino',
            'lumino', 'mesto', 'mobilino', 'morso', 'modellino', 'modello',
            'oggettivo', 'oracolo', 'padellino', 'parlamento', 'passeggino',
            'pendolino', 'pisolino', 'pompino', 'profumino', 'provino',
            'regolamento', 'reimpianto', 'rinvio', 'riposino', 'riso',
            'ritocchino', 'ruttino', 'scheletro', 'scherno', 'sedano', 'slittino',
            'soluto', 'sorriso', 'stato', 'stoppino', 'successo', 'tagliando',
            'tamburino', 'tango', 'transatto', 'unto', 'vallo', 'vicario'],
        'Q': ['abiura', 'accetta', 'accusa', 'adultera', 'amnistia', 'ancora',
            'angoscia', 'anima', 'ara', 'area', 'arma', 'asfissia', 'aureola',
            'avventura', 'balestra', 'balletta', 'barzelletta', 'branda',
            'bulletta', 'cadenza', 'calamita', 'cantilena', 'capotta',
            'carambola', 'carpa', 'carrozza', 'carrucola', 'catapulta',
            'chiacchiera', 'coccola', 'cola', 'congrega', 'consegna', 'consocia',
            'controfirma', 'controreplica', 'convalida', 'cricca', 'cripta',
            'cucina', 'delibera', 'deroga', 'disputa', 'divisa', 'domanda',
            'droga', 'era', 'esca', 'fata', 'fatica', 'federa', 'fionda',
            'fodera', 'frana', 'gomma', 'idea', 'idrata', 'imposta', 'impronta',
            'inchiesta', 'insegna', 'intervista', 'isola', 'libra', 'linea',
            'maschera', 'meraviglia', 'mira', 'mitraglia', 'ombra', 'opera',
            'orbita', 'orchestra', 'padella', 'pattuglia', 'pausa', 'permesso',
            'pesca', 'pipa', 'procura', 'propaganda', 'prova', 'quadrella',
            'ratifica', 'recita', 'recluta', 'ricompensa', 'riconferma',
            'ricorso', 'riforma', 'rima', 'scadenza', 'schiera', 'scorza',
            'seghetta', 'setola', 'sfera', 'sfida', 'sgombera', 'sia', 'soletta',
            'sonda', 'spesa', 'spira', 'statua', 'stia', 'stoppa', 'stufa',
            'tempera', 'tesa', 'tonda', 'ulcera', 'urgenza', 'urina', 'valuta',
            'vena', 'vendemmia', 'visita', 'voglia'],
        'R': [],
        'S': ['abbagliante', 'abbondante', 'abbracciante', 'abbronzante',
            'aberrante', 'abitante', 'accattivante',  'accogliente',
            'accomodante', 'accondiscendente', 'acconsenziente', 'acetificante',
            'acidificante', 'addensante', 'aderente', 'affluente', 'agente',
            'amante', 'avvincente', 'compare', 'contundente', 'corrispondente',
            'defoliante', 'dipendente', 'dirompente', 'disobbediente',
            'disubbidiente', 'divertente', 'ente', 'esponente', 'estenuante',
            'favore', 'garante', 'ignorante', 'imbarazzante', 'incivile',
            'indice', 'inerente', 'infertile', 'insegnante', 'insigne',
            'negligente', 'obbediente', 'ode', 'sapiente', 'sapore', 'senziente',
            'sfavore', 'sofferente', 'sole', 'tangente', 'ubbidiente'],
        'n': ['angoscia', 'interfaccia', 'pronuncia'],
        'o': ['abortivo', 'acconcio', 'acidulo', 'adatto', 'antico', 'attento',
            'attivo', 'azzurro', 'buffo', 'calmo', 'carino', 'complesso',
            'contento', 'contrario', 'corso', 'decimo', 'degno', 'deluso',
            'diverso', 'divo', 'duro', 'edito', 'esatto', 'esterno', 'estivo',
            'eterno', 'falso', 'finto', 'foggiano', 'franco', 'freddino',
            'freddo', 'funesto', 'interno', 'lacero', 'libero', 'mesto', 'misero',
            'montano', 'muto', 'oggettivo', 'parso', 'pugnato', 'ricolmo',
            'scaltro', 'scomparso', 'scosceso', 'sgombero', 'sgombro', 'sgomento',
            'sincero', 'sollecito', 'stanco', 'stretto', 'stufo', 'stupendo',
            'successo', 'tacito', 'tondo', 'torto', 'trito', 'ubriaco', 'ultimo',
            'valgo', 'vario'],
        'p': ['amico', 'astrologo', 'autentico', 'estrinseco', 'organico'],
        None: ['abbasso', 'addosso', 'azoto', 'cromo', 'dai', 'eclissi', 'paia',
            'paio', 'rimpetto', 'sei', 'strutto', 'tanga'],
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
#    (xx, RimuoviVerbi(label="Togli tutti i verbi!!!",)),
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
