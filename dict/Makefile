DICTFILES = italian_ispell.dict italian_ispell.affix italian_ispell.stop

dict : $(DICTFILES)

VERSION =  $(shell cat ../VERSION)

ifndef DATE
DATE = $(shell date +%Y-%m-%d)
endif

FILTER_VAR = \
	  sed 's,VERSION,$(VERSION),g' \
	| sed 's,DATE,$(DATE),g'

HEADER : HEADER.in
	cat $< | $(FILTER_VAR) > $@

italian_ispell.dict : italian-verbs.dict italian-other.dict italian-numbers.dict HEADER
	sed 's,^,/ ,' < HEADER > $@
	python merge_dicts.py \
		italian-verbs.dict italian-other.dict italian-numbers.dict >> $@

italian_ispell.affix : italian.aff.before-verbs italian.aff.verbs italian.aff.after-verbs HEADER
	sed 's,^,/ ,' < HEADER > $@
	cat italian.aff.before-verbs italian.aff.verbs italian.aff.after-verbs >> $@

italian_ispell.stop : italian.stop
	cat $< > $@

clean:
	rm -rf $(DICTFILES) HEADER

split:
	python ./split_dict.py

merge:
	python merge_dicts.py verbi.dict italian-other.dict italian-numbers.dict > italian.dict
	cat italian.aff.before-verbs verbi.aff italian.aff.after-verbs > italian.aff

