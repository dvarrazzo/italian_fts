DISTNAME = italian-fts
VERSION =  $(shell cat ../VERSION)
ifndef DATE
DATE = $(shell date +%Y-%m-%d)
endif

PKGFILES = $(DISTNAME)-$(VERSION)-latin1.tar.gz \
           $(DISTNAME)-$(VERSION)-utf8.tar.gz
PAGES = italian-fts.html fts-italiano.html index.html \
	README.italian_fts_utf8.html README.italian_fts_latin1.html \
	LEGGIMI.italian_fts_utf8.html LEGGIMI.italian_fts_latin1.html 


.PHONY : clean

site : site.tar.gz

upload : site.tar.gz
	scp $< piro@trinity.develer.com:public_html/ispell-italian

FILTER_VAR = \
	  sed 's,VERSION,$(VERSION),g' \
	| sed 's,DATE,$(DATE),g' 

FILTER_UTF8 = \
	  sed 's,ENCODING,utf8,g'

FILTER_LATIN1 = \
	  sed 's,ENCODING,latin1,g'

site.tar.gz: $(PKGFILES) $(PAGES)
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

LEGGIMI.italian_fts_utf8.html : ../LEGGIMI.italian_fts.in
	cat $< | $(FILTER_VAR) | $(FILTER_UTF8) | rst2html.py --lang=it > $@
	
LEGGIMI.italian_fts_latin1.html : ../LEGGIMI.italian_fts.in
	cat $< | $(FILTER_VAR) | $(FILTER_LATIN1) | rst2html.py --lang=it > $@

$(DISTNAME)-$(VERSION)-utf8.tar.gz : ../dist/$(DISTNAME)-$(VERSION)-utf8.tar.gz 
	$(MAKE) -C .. ENCODING=utf8 package
	ln $< $@

$(DISTNAME)-$(VERSION)-latin1.tar.gz : ../dist/$(DISTNAME)-$(VERSION)-latin1.tar.gz 
	$(MAKE) -C .. ENCODING=latin1 package
	ln $< $@

clean:
	-rm $(PAGES) $(PKGFILES) site.tar.gz
