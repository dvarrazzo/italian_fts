# italian_fts -- pgxs-based makefile
#
# Copyright (C) 2007-2011 Daniele Varrazzo

PG_CONFIG = pg_config

EXTENSION = italian_fts
EXTVERSION = $(shell grep '"version":' META.json | head -1 | sed -e 's/\s*"version":\s*"\(.*\)",/\1/')
PG91 = $(shell $(PG_CONFIG) --version | grep -qE " 8\.| 9\.0" && echo pre91 || echo 91)

DATA_TSEARCH = italian.dict italian.affix italian.stop
DOCS = README.$(EXTENSION) LEGGIMI.$(EXTENSION)

ifeq ($(PG91),91)
INSTALLSCRIPT = $(EXTENSION)--$(EXTVERSION).sql
else
INSTALLSCRIPT = $(EXTENSION).sql
endif

$(EXTENSION)--$(EXTVERSION).sql : $(EXTENSION).sql
	cp $< $@

DATA = $(INSTALLSCRIPT)

USE_PGXS=1
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)

install : $(INSTALLSCRIPT)
