DICTFILES = italian.dict italian.affix

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

italian.dict : italian-verbs.dict italian-other.dict italian-numbers.dict HEADER
	sed 's,^,/ ,' < HEADER > $@
	python merge_dicts.py \
		italian-verbs.dict italian-other.dict italian-numbers.dict >> $@

italian.affix : italian.aff.before-verbs italian.aff.verbs italian.aff.after-verbs HEADER
	sed 's,^,/ ,' < HEADER > $@
	cat italian.aff.before-verbs italian.aff.verbs italian.aff.after-verbs >> $@

clean:
	rm -rf $(DICTFILES) HEADER

split:
	python ./split_dict.py

merge:
	python merge_dicts.py verbi.dict italian-other.dict italian-numbers.dict > italian.dict
	cat italian.aff.before-verbs verbi.aff italian.aff.after-verbs > italian.aff

