EXTENSION = italian_fts
DOCFILES = README.rst LEGGIMI.rst COPYING CHANGES \
	META.json $(EXTENSION).control
SRCFILES = Makefile $(EXTENSION).sql uninstall_$(EXTENSION).sql
DICTFILES = italian_ispell.dict italian_ispell.affix italian_ispell.stop
DISTFILES = $(addprefix build/, $(SRCFILES) $(DOCFILES) $(DICTFILES))

VERSION =  $(shell cat VERSION)
PKGNAME = $(EXTENSION)-$(VERSION)
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

FILTER_VAR = \
	  sed 's,VERSION,$(VERSION),g' \
	| sed 's,DATE,$(DATE),g'

build/% : src/%.in
	cat $< | $(FILTER_VAR) > $@

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

