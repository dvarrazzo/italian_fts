DISTNAME = ispell-italian
VERSION = 1.0

PKGFILE = $(DISTNAME)-$(VERSION)

DICTFILES = ../italian.dict ../italian.aff ../italian.stop
DOCSOURCE = ../README.txt ../LEGGIMI.txt gpl.txt

site.tar.gz: $(PKGFILE).tar.gz italian-fts.html fts-italiano.html
	tar czvf $@ $^

$(PKGFILE).tar.gz : $(DICTFILES) $(DOCSOURCE)
	-mkdir $(PKGFILE)
	cp $(DICTFILES) $(DOCSOURCE) $(PKGFILE)
	tar czvf $@ $(PKGFILE)

italian-fts.html: ../README.txt
	rst2html.py < $< > $@

fts-italiano.html: ../LEGGIMI.txt
	rst2html.py --lang=it < $< > $@

