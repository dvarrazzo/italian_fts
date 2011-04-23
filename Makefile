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

ICONV = iconv -f latin1 -t utf8

.PHONY : dict package site clean

sdist : dict $(PKGFILE)

dict :
	$(MAKE) -C dict $@

site :
	$(MAKE) -C site $@

package: $(PKGFILE)

build/% : src/%
	@mkdir -p build
	cat < $< > $@

build/% : %
	@mkdir -p build
	cat < $<  > $@

build/% : dict/%
	cat $< | $(ICONV) > $@

$(PKGFILE) : $(DISTFILES)
	mkdir -p dist
	ln -s build $(PKGNAME)
	rm -rf $@
	tar czvf $@ $(patsubst build/%,$(PKGNAME)/%,$^)
	rm $(PKGNAME)

clean:
	rm -rf build
	$(MAKE) -C dict $@

