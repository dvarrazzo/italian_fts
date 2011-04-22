DATAFILES = italian.dict italian.affix italian_ispell.stop
DOCFILES = README.italian_fts LEGGIMI.italian_fts
SQLFILES = italian_fts.sql

SHAREDIR = $(shell pg_config --sharedir)
DOCDIR = $(shell pg_config --docdir)
DICTDIR = $(SHAREDIR)/tsearch_data

install :
	cp $(DATAFILES) $(DICTDIR)
	cp $(DOCFILES) $(DOCDIR)
	cp $(SQLFILES) $(SHAREDIR)
