import re

class Production(object):
    def __init__(self, pattern="", remove="", append=""):
        pt = ''.join(pattern.split()).lower()
        if not pt.endswith(remove.lower()):
            raise ValueError("can't remove '%s' from a word matching '%s'"
                % (remove, pt))
        self._regexp = re.compile(pattern+'$', re.VERBOSE | re.IGNORECASE)
        self.pattern = pt
        self.remove = remove.lower()
        self.append = append.lower()

        self.comment = None
        self.line_comment = None
        self.enabled = True

    def matches(self, word):
        return bool(self._regexp.search(word))

    def apply(self, word):
        if self.matches(word):
            return word[:len(word)-len(self.remove)] + self.append
        else:
            raise ValueError("the word '%s' doesn't match the pattern '%s'"
                % (word, self.pattern))

    def __add__(self, other):
        if not self.append.endswith(other.remove):
            raise ValueError(
                "can't compose a %s appending '%s' with one removing '%s'"
                % (self.__class__.__name__, self.append, other.remove))

        return self.__class__(self.pattern, self.remove,
            self.append[:len(self.append)-len(other.remove)] + other.append)

    def __iadd__(self, other):
        tmp = self + other
        self.append = tmp.append

    def __repr__(self):
        return ("<%s (%s > %s%s) at 0x%08X>"
            % (self.__class__.__name__,
                self.pattern or '.',
                self.remove and ("-%s," % self.remove),
                self.append,
                id(self)))

    def __str__(self):
        if not self.pattern:
            o = '.'
        elif self.pattern.startswith("["):
            a,b = self.pattern.split("]", 1)
            o = a + "] " + " ".join(b)
        else:
            o = " ".join(self.pattern)

        o = "    %s" % o
        o = "%s%*s >" % (o, len(o)-19, "")
        o = "%s    %s%s" % (
            o, self.remove and ("-%s," % self.remove), self.append)
        if not self.enabled:
            o = "# " + o

        return self._addComment(o)

    def _addComment(self, string):
        # bug in the tsearch2 parser: if there is no string to append,
        # an inline comment causes a parse error.
        if self.line_comment and (self.append or not self.enabled):
            string = "%s%*s# %s" % (
                string, len(string)-40, "", self.line_comment)
        if self.comment is None:
            return string
        else:
            lo = []
            for row in self.comment.split('\n'):
                lo.append("\n    # %s" % row)
            return "%s\n%s" % ("".join(lo), string)

class Prefix(Production):
    def __init__(self, pattern="", remove="", append=""):
        pt = ''.join(pattern.split()).lower()
        if not pt.startswith(remove.lower()):
            raise ValueError("can't remove '%s' from a word matching '%s'"
                % (remove, pt))
        self._regexp = re.compile('^'+pattern, re.VERBOSE | re.IGNORECASE)
        self.pattern = pt
        self.remove = remove.lower()
        self.append = append.lower()

        self.comment = None
        self.line_comment = None
        self.enabled = True

    def apply(self, word):
        if self.matches(word):
            return self.append + word[len(self.remove):]
        else:
            raise ValueError("the word '%s' doesn't match the pattern '%s'"
                % (word, self.pattern))

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

class Difettivo(Production):
    def __str__(self):
        return self._addComment("# difettivo")

class Flag(object):
    def __init__(self, letter, allow_prefix=True):
        self.letter = letter
        self.allow_prefix = allow_prefix
        self.productions = []
        self.comment = None
        self.verbs = []

    def __repr__(self):
        return ("<%s '%s' (%s prod.) at 0x%08X>"
            % (self.__class__.__name__,
                self.letter,
                len(self.productions),
                id(self)))

    def __str__(self):
        o = map(str, self.productions)
        o.insert(0, "flag %s%s:" % (self.allow_prefix and '*' or '',
                                    self.letter))

        if self.comment:
            o[:0] = [ "# %s" % r for r in self.comment.split('\n') ]

        return '\n'.join(o)

    def apply(self, word):
        return [ p.apply(word) for p in self.productions if p.matches(word) ]


class Affixes(dict):
    def apply(self, word, flags):
        pres = []
        sufs = []

        for f in flags:
            if f not in self: continue
            prod = self[f]
            if not prod.productions: continue

            if isinstance(prod.productions[0], Prefix):
                pres.append(prod)
            else:
                sufs.append(prod)

        o = []
        for suf in sufs:
            nwords = suf.apply(word)
            o += nwords

            if suf.allow_prefix:
                for pre in pres:
                    for w in nwords:
                        o += pre.apply(w)

        return o

def parseIspellAff(f):
    flags = []

    prod_class = Production

    re_flag = re.compile(r'\s*flag\s+([*]?)\\?(.)\:')
    re_prod = re.compile(r"([^>]+)>\s+(?:-\s*([^,]*)\s*)?\s*[,]?\s*([^,]*)")

    flag = None
    for i, row in enumerate(f):
        f = row.split('#', 1)[0].rstrip()
        if not f: continue

        m = re_flag.match(f)
        if m is not None:
            flag = Flag(letter=m.group(2), allow_prefix=bool(m.group(1)))
            flags.append(flag)
            continue

        m =  re_prod.match(f)
        if m is not None:
            if flag is None:
                raise Exception("production w/o flag at line %d" % (i+1))

            ptrn, pre, suf = m.groups()
            if ptrn == '.': ptrn = ''
            pre = pre and pre.rstrip() or ''
            suf = suf and suf.rstrip() or ''
            flag.productions.append(prod_class(ptrn, remove=pre, append=suf))

        if f == 'prefixes':
            prod_class = Prefix

    return Affixes((flag.letter, flag) for flag in flags)
