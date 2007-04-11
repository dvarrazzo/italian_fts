from affix import Production

def compose(p1, p2):
    a = None
    if (p1.append in ('mi', 'ti', 'ci', 'vi', 'si')
        and p2.append in ('lo', 'la', 'li', 'le', 'ne')):
        a = Production('i', remove='i', append='e')
    elif (p1.append in ('gli',)
        and p2.append in ('lo', 'la', 'li', 'le', 'ne')):
        a = Production('i', remove='', append='e')

    if a is None:
        return p1 + p2
    else:
        return p1 + a + p2

imp2s_r = [ Production(append=_) for _ in ('mi', 'gli', 'ti', 'ci') ]
imp2s_p = [ Production(append=_) for _ in ('lo', 'la', 'li', 'le', 'ne') ]
imp2s_rp = [ compose(p1, p2) for p1 in imp2s_r for p2 in imp2s_p ]

imp1p_r = [ Production(append=_) for _ in ('gli', 'ci') ]
imp1p_p = [ Production(append=_) for _ in ('lo', 'la', 'li', 'le', 'ne') ]
imp1p_rp = [ compose(p1, p2) for p1 in imp1p_r for p2 in imp1p_p ]

imp2p_r = [ Production(append=_) for _ in ('mi', 'gli', 'ci', 'vi') ]
imp2p_p = [ Production(append=_) for _ in ('lo', 'la', 'li', 'le', 'ne') ]
imp2p_rp = [ compose(p1, p2) for p1 in imp2p_r for p2 in imp2p_p ]

ppr_n = [ Production(), Production("e", remove="e", append="i") ]
ppr_r = [ compose(p1, Production(append='si')) for p1 in ppr_n ]

ppa_n = [Production()] + [Production("o", remove="o", append=_) for _ in 'aie']
ppa_r = [ compose(p1, Production(append=_))
            for p1 in ppa_n for _ in ('mi', 'ti', 'gli', 'ci', 'vi', 'si') ]
ppa_p = [ compose(p1, Production(append=_))
            for p1 in ppa_n for _ in ('lo', 'la', 'li', 'le', 'ne') ]
ppa_rp = [ p1 + compose(Production(append='vi'), Production(append='ne'))
            for p1 in ppa_n ]

inf1_n = [ Production('[aei]re') ]
inf1_t = [ Production('[aei]re', remove='e') ]
inf1_r = [ Production('[aei]re', remove='e', append=_)
            for _ in ('mi', 'ti', 'gli', 'ci', 'vi', 'si') ]
inf1_p = [ Production('[aei]re', remove='e', append=_)
            for _ in ('lo', 'la', 'li', 'le', 'ne') ]
inf1_rp = [ Production('[aei]re', remove='e')
            + compose(Production(append=s1), Production(append=s2))
            for s1 in ('mi', 'ti', 'gli', 'ci', 'vi', 'si')
            for s2 in ('lo', 'la', 'li', 'le', 'ne', 'si')
            if (s1, s2) != ('si', 'si')]

inf2_n = [ Production('rre') ]
inf2_t = [ Production('rre', remove='re') ]
inf2_r = [ Production('rre', remove='re', append=_)
            for _ in ('mi', 'ti', 'gli', 'ci', 'vi', 'si') ]
inf2_p = [ Production('rre', remove='re', append=_)
            for _ in ('lo', 'la', 'li', 'le', 'ne') ]
inf2_rp = [ Production('rre', remove='re')
            + compose(Production(append=s1), Production(append=s2))
            for s1 in ('mi', 'ti', 'gli', 'ci', 'vi', 'si')
            for s2 in ('lo', 'la', 'li', 'le', 'ne', 'si')
            if (s1, s2) != ('si', 'si')]

ger_r = [ Production(append=_)
            for _ in ('', 'mi', 'ti', 'gli', 'ci', 'vi', 'si') ]
ger_p = [ Production(append=_)
            for _ in ('', 'lo', 'la', 'li', 'le', 'ne', 'si') ]
ger_rp = [ compose(p1, p2)
        for p1 in ger_r for p2 in ger_p
        if not (p1.append == 'si' and p2.append == 'si') ]

superlativo = [ Production('o', remove='o', append='issimo')
                + Production('o', remove='o', append=_)
                for _ in 'oaie' ]
