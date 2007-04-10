import re

class Production(object):
    def __init__(self, pattern="", remove="", append=""):
        pt = ''.join(pattern.split()).lower()
        if not pt.endswith(remove):
            raise ValueError("can't remove '%s' from a word matching '%s'"
                % (remove, pt))
        self._regexp = re.compile(pattern+'$', re.VERBOSE | re.IGNORECASE)
        self.pattern = pt
        self.remove = remove
        self.append = append

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
        if self.line_comment:
            string = "%s%*s# %s" % (
                string, len(string)-40, "", self.line_comment)
        if self.comment is None:
            return string
        else:
            lo = []
            for row in self.comment.split('\n'):
                lo.append("\n    # %s" % row)
            return "%s\n%s" % ("".join(lo), string)

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
    def __init__(self, letter):
        self.letter = letter
        self.productions = []
        self.comment = None

    def __repr__(self):
        return ("<%s '%s' (%s prod.) at 0x%08X>"
            % (self.__class__.__name__,
                self.letter,
                len(self.productions),
                id(self)))

    def __str__(self):
        o = map(str, self.productions)
        o.insert(0, "flag *%s:" % self.letter)

        if self.comment:
            o[:0] = [ "# %s" % r for r in self.comment.split('\n') ]

        return '\n'.join(o)
