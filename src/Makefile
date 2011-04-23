# italian_fts -- pgxs-based makefile
#
# Copyright (C) 2007-2011 Daniele Varrazzo

PG_CONFIG = pg_config

EXTENSION = italian_fts
MODULEDIR = $(EXTENSION)
EXTVERSION = $(shell grep '"version":' META.json | head -1 | sed -e 's/\s*"version":\s*"\(.*\)",/\1/')
PG91 = $(shell $(PG_CONFIG) --version | grep -qE " 8\.| 9\.0" && echo pre91 || echo 91)

DATA_TSEARCH = italian_ispell.dict italian_ispell.affix italian_ispell.stop
DOCS = README.rst LEGGIMI.rst

# the += doesn't work if the user specified his own REGRESS_OPTS
REGRESS = --inputdir=test setup-$(PG91) italian_fts

ifeq ($(PG91),91)
INSTALLSCRIPT = $(EXTENSION)--$(EXTVERSION).sql
UNINSTALLSCRIPT =
else
INSTALLSCRIPT = $(EXTENSION).sql
UNINSTALLSCRIPT = uninstall_$(EXTENSION).sql
endif

$(EXTENSION)--$(EXTVERSION).sql : $(EXTENSION).sql
	cp $< $@

DATA = $(INSTALLSCRIPT) $(UNINSTALLSCRIPT)

USE_PGXS=1
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)

install : $(INSTALLSCRIPT)
