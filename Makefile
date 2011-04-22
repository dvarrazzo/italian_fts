ENCODING = utf8

DISTNAME = italian_fts
DISTDIR = italian_fts
DOCFILES = README.italian_fts LEGGIMI.italian_fts COPYING CHANGES
SRCFILES = Makefile italian_fts.sql
DICTFILES = italian.dict italian.affix italian.stop
DISTFILES = $(addprefix build/, $(SRCFILES) $(DOCFILES) $(DICTFILES))

VERSION =  $(shell cat VERSION)
PKGNAME = $(DISTNAME)-$(VERSION)
PKGFILE = dist/$(PKGNAME).tar.gz

ifndef DATE
DATE = $(shell date +%Y-%m-%d)
endif

PYTHON = python
ICONV = iconv -f latin1 -t $(ENCODING)
FILTER_VAR = \
	  sed 's,VERSION,$(VERSION),g' \
	| sed 's,DATE,$(DATE),g' \
	| sed 's,ENCODING,$(ENCODING),g'

.PHONY : package site clean

sdist : $(PKGFILE)

dict : $(addprefix build/,$(DICTFILES))

site :
	$(MAKE) -C site site

build/italian.dict : italian-verbs.dict italian-other.dict italian-numbers.dict HEADER.in
	@mkdir -p build
	sed 's,^,/ ,' < HEADER.in | $(FILTER_VAR) > $@
	$(PYTHON) merge_dicts.py \
		italian-verbs.dict italian-other.dict italian-numbers.dict \
		| $(ICONV) >> $@

build/italian.affix : italian.aff.before-verbs italian.aff.verbs italian.aff.after-verbs $(HEADER)
	@mkdir -p build
	sed 's,^,/ ,' < HEADER.in | $(FILTER_VAR) > $@
	cat italian.aff.before-verbs italian.aff.verbs italian.aff.after-verbs \
		| $(ICONV) >> $@

build/italian.stop : italian.stop
	@mkdir -p build
	cat $< | $(ICONV) > $@

package: $(PKGFILE)

build/% : src/%
	@mkdir -p build
	cat < $< > $@

build/% : %
	@mkdir -p build
	cat < $<  > $@

$(PKGFILE) : $(DISTFILES)
	mkdir -p dist
	ln -s build $(PKGNAME)
	rm -rf $@
	tar czvf $@ $(patsubst build/%,$(PKGNAME)/%,$^)
	rm $(PKGNAME)

clean:
	rm -rf build

split:
	python ./split_dict.py

merge:
	python merge_dicts.py verbi.dict italian-other.dict italian-numbers.dict > italian.dict
	cat italian.aff.before-verbs verbi.aff italian.aff.after-verbs > italian.aff

