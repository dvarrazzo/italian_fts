# use ``make ENCODING=utf8`` to create the utf8 version of everything
ENCODING = latin1

ifeq ($(ENCODING),utf8)
PGLOCALE = it_IT.utf8
else
PGLOCALE = it_IT
endif

DISTNAME = italian-fts
DISTDIR = italian_fts_$(ENCODING)
HEADER = HEADER.$(ENCODING) 
README = README.italian_fts.$(ENCODING) 
LEGGIMI = LEGGIMI.italian_fts.$(ENCODING) 
SQLFILE1 = italian_fts.sql.$(ENCODING)
SQLFILE2 = italian_fts_spell.sql.$(ENCODING)
SQLFILES = $(SQLFILE1) $(SQLFILE2)
MAKEFILE = src/Makefile.$(ENCODING)
DOCFILES = $(README) $(LEGGIMI) gpl.txt
DICTFILES_in = italian.dict italian.aff italian.stop
SOURCE = src/$(ENCODING)/dict_snowball.c src/$(ENCODING)/stem.c src/$(ENCODING)/stem.h

VERSION =  $(shell cat VERSION)
PKGFILE = $(DISTNAME)-$(VERSION)-$(ENCODING).tar.gz

ifndef DATE
DATE = $(shell date +%Y-%m-%d)
endif

PYTHON = python
ICONV = iconv -f latin1 -t $(ENCODING)
FILTER_VAR = \
	  sed 's,VERSION,$(VERSION),g' \
	| sed 's,DATE,$(DATE),g' \
	| sed 's,PGLOCALE,$(PGLOCALE),g' \
	| sed 's,ENCODING,$(ENCODING),g' 

%.$(ENCODING) : %
	$(ICONV) < $< > $@

%.$(ENCODING) : %.in
	cat $< | $(FILTER_VAR) > $@

DICTFILES = $(addsuffix .$(ENCODING),$(DICTFILES_in))

.PHONY : package clean

dict : $(DICTFILES)

package : dist/$(PKGFILE)

italian.dict : italian-verbs.dict italian-other.dict italian-numbers.dict $(HEADER)
	sed 's,^,/ ,' < $(HEADER) > $@
	$(PYTHON) merge_dicts.py \
		italian-verbs.dict italian-other.dict italian-numbers.dict >> $@

italian.aff : italian.aff.before-verbs italian.aff.verbs italian.aff.after-verbs $(HEADER)
	sed 's,^,# ,' < $(HEADER) > $@
	cat italian.aff.before-verbs italian.aff.verbs italian.aff.after-verbs >> $@

dist/$(PKGFILE) : $(DICTFILES) $(SQLFILES) $(DOCFILES) $(SOURCE) $(MAKEFILE)
	-mkdir dist
	-rm -rf dist/$(DISTDIR)
	mkdir dist/$(DISTDIR)
	cp $(DICTFILES) $(DOCFILES) dist/$(DISTDIR)
	cp $(SOURCE) dist/$(DISTDIR)
	cp $(SQLFILE1) dist/$(DISTDIR)/italian_fts_$(ENCODING).sql.in
	cp $(SQLFILE2) dist/$(DISTDIR)/italian_fts_spell_$(ENCODING).sql.in
	cp $(MAKEFILE) dist/$(DISTDIR)/Makefile
	tar czvf dist/$(PKGFILE) -C dist $(DISTDIR)

clean:
	-rm -rf dist/italian_fts_latin1
	-rm -rf dist/italian_fts_utf8
	-rm italian.dict italian.aff
	-rm $(addsuffix .latin1,HEADER README.italian_fts LEGGIMI.italian_fts \
	                        italian_fts.sql italian_fts_spell.sql \
							$(DICTFILES_in) src/Makefile)
	-rm $(addsuffix   .utf8,HEADER README.italian_fts LEGGIMI.italian_fts \
	                        italian_fts.sql italian_fts_spell.sql \
	                        $(DICTFILES_in) src/Makefile)

split:
	python ./split_dict.py

merge:
	python merge_dicts.py verbi.dict italian-other.dict italian-numbers.dict > italian.dict
	cat italian.aff.before-verbs verbi.aff italian.aff.after-verbs > italian.aff

