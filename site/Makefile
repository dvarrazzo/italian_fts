DISTNAME = italian_fts
VERSION =  $(shell cat ../VERSION)
ifndef DATE
DATE = $(shell date +%Y-%m-%d)
endif

PACKAGE_PG83 = $(DISTNAME)-$(VERSION).tar.gz
PACKAGES = $(PACKAGE_PG83)

PAGES = italian-fts.html fts-italiano.html index.html \
	README.html LEGGIMI.html

REMOTEDIR = piro@trinity.develer.com:public_html/ispell-italian/incoming

.PHONY : clean site_upload packages_upload

site : $(PAGES)

site_upload: site.tar.gz
	scp $< $(REMOTEDIR)

packages : $(PACKAGES)

packages_upload: $(PACKAGES)
	scp $^ $(REMOTEDIR)

FILTER_VAR = \
	  sed 's,VERSION,$(VERSION),g' \
	| sed 's,DATE,$(DATE),g' 

site.tar.gz: $(PACKAGES) $(PAGES)
	tar czvf $@ $^

index.html : fts-italiano.html
	cp $< $@

italian-fts.html: italian-fts.txt
	cat $< | $(FILTER_VAR) | rst2html.py > $@

fts-italiano.html: fts-italiano.txt
	cat $< | $(FILTER_VAR) | rst2html.py --lang=it > $@

README.html : ../README.rst
	rst2html.py < $< > $@

LEGGIMI.html : ../LEGGIMI.rst
	rst2html.py < $< > $@

$(PACKAGE_PG83) : ../dist/$(PACKAGE_PG83)
	$(MAKE) -C .. sdist
	ln $< $@

clean:
	rm -f $(PAGES) $(PACKAGES) site.tar.gz
