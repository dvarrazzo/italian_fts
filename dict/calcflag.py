#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import affix

def calcFlags(forms):
    # Cerca il suffisso di maggior lunghezza comune a tutta la classe
    # ---------------------------------------------------------------

    max_suf = {}
    for k, v in forms.iteritems():
        for i in range(len(v[0]), -1, -1):
            if sum(map(lambda _: _.endswith(v[0][i:]), v)) != len(v):
                i += 1
                break
        max_suf[k] = v[0][i:]

        # Cerca di anteporre un pattern per la prima lettera variabile
        try:
            prefs = sorted(set([_[i-len(v[0])-1] for _ in v]))
        except:
            pass
        else:
            if 1 or len(prefs) <= 4:
                max_suf[k] = "[%s]%s" % (''.join(prefs), max_suf[k])


    # Raduna la classi compatibili in flag
    # ------------------------------------

    def espandi(s):
        """Espandi una stringa rappresentante un pattern in una lista di insiemi.

        Spacializzata in pattern tipo ``abc`` o ``[abc]de``, non generica.
        """
        if "]" in s:
            s1, s2 = s.split("]",1)
            return [ set(s1[1:]) ] + [ set(l) for l in s2 ]
        else:
            return [ set(l) for l in s ]

    def collidono(s1, s2):
        e1 = espandi(s1)
        e2 = espandi(s2)
        for i in range(-1, -min(len(e1), len(e2))-1, -1):
            if not e1[i] & e2[i]:
                return False
        else:
            return True

    def compatibile(s, L):
        """Verifica se il suffisso s è compatibile con la lista L

        Un suffisso è compatibile se esiste un *suo* suffisso distinto
        in tutta la lista.
        """
        for s2 in L:
            if collidono(s, s2):
                return False
        else:
            return True

    flags = []
    for k, v in sorted(forms.iteritems(), key=lambda _: len(_[1]), reverse=True):
        suf = max_suf[k]
        for flag in flags:
            if compatibile(suf, flag.values()):
                flag[k] = suf
                break
        else:
            flags.append({k: suf})


    # Riduci i pattern dei flag al minimo indispensabile
    # --------------------------------------------------

    def riduciSuffisso(suf, L, mlen):
        """Riduci al minimo un suffisso mantenendolo compatibile con la lista L"""
        if "]" in suf:
            s1, s2 = suf.split("]",1)
            suf = [ s1 + "]" ] + list(s2)
        else:
            suf = list(suf)

        good = suf
        while suf and len(suf) > mlen:
            suf = suf[1:]
            if not compatibile(''.join(suf), L):
                break
            good = suf

        return ''.join(good)

    for flag in flags:
        sufs = set(flag.itervalues())
        for k, suf in sorted(flag.iteritems(), key=lambda _: _[1]):
            # Evita che il suffisso diventi più corto della parte da rimuovere
            mlen = k and max( len(p[0]) for p in k if p) or 0
            sufs.remove(suf)
            suf = riduciSuffisso(suf, sufs, mlen)
            flag[k] = suf
            sufs.add(suf)


    # Metti in negativo i pattern grandi
    # ----------------------------------

    for flag in flags:
        for k, suf in list(flag.iteritems()):
            if not (suf.startswith('[') and suf[1] != '^' and suf.index("]") > 5):
                continue

            s1, s2 = suf.split("]", 1)
            used = []
            for suf2 in list(flag.values()):
                if suf2 == suf:
                    continue

                if not (suf2.endswith(s2) and len(suf) > len(s2)):
                    continue

                if suf2[-(len(s2)+1)] != "]":
                    used.append(suf2[-(len(s2)+1)])
                else:
                    assert suf2[1] != '^'
                    used.append(suf2.split(']',1)[0][1:])

            flag[k] = "[^%s]%s" % (''.join(sorted(set(''.join(used)))), s2)

    return flags

def toFlags(fin, avail, examples={}):
    fout = []
    for f in fin:
        fo = affix.Flag(avail.pop(0))
        fout.append(fo)
        for k, suf in sorted(f.iteritems(),
                key=lambda _: _[0] in examples
                              and -len(examples[_[0]]) or 0):
            first_prod = True
            distincts = set()
            for pair in k:
                if pair is None:
                    p = affix.Difettivo()
                    fo.productions.append(p)

                else:
                    p = affix.Production(suf, remove=pair[0], append=pair[1])
                    fo.productions.append(p)

                    if pair in distincts:
                        p.enabled = False
                    else:
                        distincts.add(pair)

                verbs = examples.get(k)
                if not (first_prod and verbs): continue

                verbs.sort()
                fo.verbs.extend(verbs)

                i = 1
                while i <= len(verbs):
                    i += 1
                    if 70 < sum(map(len, verbs[:i+1])) + 2 * (i):
                        break

                p.comment = ", ".join(verbs[:i])
                if i <= len(verbs):
                    p.comment += "..."

                p.comment = ("flag *%s: # %s\n" % (fo.letter, p.pattern )
                             + p.comment)

                first_prod = False

    return fout
