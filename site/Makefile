DISTNAME = italian-fts
VERSION =  $(shell cat ../VERSION)
ifndef DATE
DATE = $(shell date +%Y-%m-%d)
endif

PACKAGE_UTF8 = $(DISTNAME)-$(VERSION)-utf8.tar.gz
PACKAGE_LATIN1 = $(DISTNAME)-$(VERSION)-latin1.tar.gz
PACKAGE_PG83 = $(DISTNAME)-$(VERSION).tar.gz
PACKAGES = $(PACKAGE_UTF8) $(PACKAGE_LATIN1) $(PACKAGE_PG83)

PAGES = italian-fts.html fts-italiano.html index.html \
	README.italian_fts_utf8.html README.italian_fts_latin1.html \
	LEGGIMI.italian_fts_utf8.html LEGGIMI.italian_fts_latin1.html \
	README.italian_fts.html LEGGIMI.italian_fts.html \

REMOTEDIR = piro@trinity.develer.com:public_html/ispell-italian/incoming

.PHONY : clean upload_site upload_packages

site : $(PAGES)

site_upload: site.tar.gz
	scp $< $(REMOTEDIR)

packages : $(PACKAGES)

packages_upload: $(PACKAGES)
	scp $^ $(REMOTEDIR)

FILTER_VAR = \
	  sed 's,VERSION,$(VERSION),g' \
	| sed 's,DATE,$(DATE),g' 

FILTER_UTF8 = \
	  sed 's,ENCODING,utf8,g'

FILTER_LATIN1 = \
	  sed 's,ENCODING,latin1,g'

site.tar.gz: $(PACKAGES) $(PAGES)
	tar czvf $@ $^

index.html : fts-italiano.html
	cp $< $@

italian-fts.html: italian-fts.txt
	cat $< | $(FILTER_VAR) | rst2html.py > $@

fts-italiano.html: fts-italiano.txt
	cat $< | $(FILTER_VAR) | rst2html.py --lang=it > $@

README.italian_fts_utf8.html : ../README.italian_fts.in
	cat $< | $(FILTER_VAR) | $(FILTER_UTF8) | rst2html.py > $@
	
README.italian_fts_latin1.html : ../README.italian_fts.in
	cat $< | $(FILTER_VAR) | $(FILTER_LATIN1) | rst2html.py > $@

README.italian_fts.html : ../README.italian_fts_pg83.in
	cat $< | $(FILTER_VAR) | $(FILTER_LATIN1) | rst2html.py > $@

LEGGIMI.italian_fts_utf8.html : ../LEGGIMI.italian_fts.in
	cat $< | $(FILTER_VAR) | $(FILTER_UTF8) | rst2html.py --lang=it > $@
	
LEGGIMI.italian_fts_latin1.html : ../LEGGIMI.italian_fts.in
	cat $< | $(FILTER_VAR) | $(FILTER_LATIN1) | rst2html.py --lang=it > $@

LEGGIMI.italian_fts.html : ../LEGGIMI.italian_fts_pg83.in
	cat $< | $(FILTER_VAR) | $(FILTER_UTF8) | rst2html.py --lang=it > $@

$(PACKAGE_UTF8) : ../dist/$(PACKAGE_UTF8)
	$(MAKE) -C .. ENCODING=utf8 package
	ln $< $@

$(PACKAGE_LATIN1) : ../dist/$(PACKAGE_LATIN1) 
	$(MAKE) -C .. ENCODING=latin1 package
	ln $< $@

$(PACKAGE_PG83) : ../dist/$(PACKAGE_PG83)
	$(MAKE) -C .. -f Makefile.pg83 package
	ln $< $@

clean:
	-rm $(PAGES) $(PACKAGES) site.tar.gz
