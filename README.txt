=======================================
Italian Dictionary for Full Text Search
=======================================

:Author: Daniele Varrazzo
:Contact: piro (at) develer.com
:Organization: `Develer S.r.l. <http://www.develer.com>`__
:Date: 2007-04-25
:Version: 1.0

:Abstract: This package provides a dictionary and the other files required to
    perform *full text search* in Italian documents using the PostgreSQL_
    database together with the contrib module Tsearch2_.

    Using the provided dictionary, search operations in Italian documents can
    keep into account the possible variations of Italian words, such as verb
    conjugations.

    .. _PostgreSQL: http://www.postgresql.org
    .. _Tsearch2: http://www.sai.msu.su/~megera/postgres/gist/tsearch/V2/


:Copyright: 2001, 2002 Gianluca Turconi
:Copyright: 2002, 2003, 2004 Gianluca Turconi and Davide Prina
:Copyright: 2004, 2005, 2006 Davide Prina
:Copyright: 2007 Daniele Varrazzo

[ `Versione italiana <fts-italiano.html>`__ ]


This file is distributed under GPL license.

This file is part of the Italian dictionary for full-text search.

The Italian dictionary for full-text search is free software; you can
redistribute it and/or modify it under the terms of the GNU General Public
License as published by the Free Software Foundation; either version 2 of
the License, or (at your option) any later version.

The Italian dictionary for full-text search is distributed in the hope that
it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public
License along with Italian dictionary for full-text search,
if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

GPL license can be found at http://www.fsf.org/licenses/licenses.html


.. Contents::


Dictionary informations
=======================

This vocabulary has been generated from the MySpell OpenOffice.org vocabulary,
provided by the `progetto linguistico`_.

.. _progetto linguistico: http://linguistico.sourceforge.net/

The dictionary had to undergo an huge amount of transformations, and is now
quite unrecognizable from the original. Above all, all the verbal forms,
including irregular verbs, are now reduced to the infinite form. Furthermore,
for each verb, the construction with pronominal and reflexive particles are
recognized on gerund, present and past participle, imperative and infinite.

Great care has also been taken in reducing the different forms of adjectives
(male and female, singular and plural, superlatives) to a single normal form,
and to unify different forms of male and female (es. *ricercatore* and
*ricercatrice*: male and female form of "researcher").

Furthermore, in the original dictionary, many unrelated male and female nouns
were joined together as they were an adjective (es. *caso/casi* + *casa/case*,
with the unrelated meanings of "case(s)" and "house(s)"). Such false friends
have been mostly split apart to avoid false positives in search results, but
some of them may still lie around in the dictionary (this is a kind of error
that no Python script can help fixing...).

Some statistics about the current dictionary edition:

- **66,929** distinct roots,
- **7,300** completely conjugated verbs
- **1,943,826** distinct recognized terms
- **62** flags in the affix file
- **10,365** production rules in the affix file.


Download
========

This dictionary release can be downloaded from the URL:

http://www.develer.com/~piro/ispell-italian/ispell-italian-1.0.tar.gz

You can check on the project page if new dictionary versions are available.


Dictionary installation
=======================

The package contains the following files:

``italian.dict``
    list of Italian words, with flags indicating the possible word variations;

``italian.aff``
    ISpell format file describing the available word variations;

``italian.stop``
    list of the stop-words to be excluded from the search because without
    meaning on their own (such as conjunctions, articles...)

The file encoding is ``iso-8859-1`` (aka ``latin1``). This means that the
dictionary can be successfully installed into a database created with
``LATIN1`` encoding. If you want to use the dictionary with an ``UTF8`` encoded
database you can perform file conversion using::

    $ iconv -f latin1 -t utf8 < italian.dict > italian_UTF8.dict
    $ iconv -f latin1 -t utf8 < italian.aff  > italian_UTF8.aff
    $ iconv -f latin1 -t utf8 < italian.stop > italian_UTF8.stop

You may read many useful informations in online documentation about using
`Tsearch2 and Unicode/UTF-8`__.

.. __: http://www.sai.msu.su/~megera/postgres/gist/tsearch/V2/
            docs/tsearch2_german_utf8.html

Whatever set of file you want to use, you must copy them into a directory
that can be read by the PostgreSQL backend. In this document the directory
``/usr/share/postgresql`` will be used as example: if you choose a different
directory, please change the instructions accordingly.


Configuration
=============


TSearch2 installation
---------------------

We shall assume that the Tsearch2 library has been installed as described
in its documentation__. If you have done it correctly, the following tables
should be present in your database::

    tstest=# \d
            List of relations
     Schema |     Name     | Type  | Owner
    --------+--------------+-------+-------
     public | pg_ts_cfg    | table | piro
     public | pg_ts_cfgmap | table | piro
     public | pg_ts_dict   | table | piro
     public | pg_ts_parser | table | piro
    (4 rows)

.. __: http://www.sai.msu.su/~megera/postgres/gist/tsearch/V2/
            docs/tsearch-V2-intro.html


Dictionary configuration
------------------------

The dictionary has to be configured in the ``pg_ts_dict`` table. You must
replace the values in the ``dict_initoption`` fields with the path and
filenames of the files you have chosen::

    tstest=# INSERT INTO pg_ts_dict
        (dict_name, dict_comment, dict_init, dict_lexize, dict_initoption)

        SELECT 'it_spell', 'Italian spelling dictionary',
            dict_init, dict_lexize,
            'DictFile="/usr/share/postgresql/italian.dict",'
            'AffFile="/usr/share/postgresql/italian.aff",'
            'StopFile="/usr/share/postgresql/italian.stop"'

        FROM pg_ts_dict
        WHERE dict_name = 'ispell_template';

    INSERT 16627 1

You can check the if the dictionary is properly working performing lexization
of a couple of terms::

    tstest=# SELECT lexize('it_spell', 'Mangiato');
       lexize
    ------------
     {mangiare}
    (1 row)

    tstest=# SELECT lexize('it_spell', 'ma');
     lexize
    --------
     {}
    (1 row)

The first query shows a conjugated verb traced to the infinite form. The
second query tests shows that stop-words are correctly discarded.

Configuration is completed with the creation of a mapping from the parsed
tokens to the dictionary::

    tstest=# INSERT INTO pg_ts_cfg (ts_name, prs_name, locale)
            VALUES ('default_italian', 'default', 'it_IT');
    INSERT 16630 1

    tstest=# INSERT INTO pg_ts_cfgmap
            SELECT 'default_italian', tok_alias, dict_name
            FROM pg_ts_cfgmap
            WHERE ts_name = 'simple';
    INSERT 0 19

    tstest=# UPDATE pg_ts_cfgmap
            SET dict_name = '{it_spell,simple}'
            WHERE ts_name = 'default_italian'
            AND tok_alias IN ('word', 'lword', 'nlword',
                'part_hword', 'lpart_hword', 'nlpart_hword');
    UPDATE 6

    tstest=# UPDATE pg_ts_cfgmap
            SET dict_name = NULL
            WHERE ts_name = 'default_italian'
            AND tok_alias IN ('hword', 'lhword', 'nlhword');
    UPDATE 3

The value chosen from the ``pg_ts_cfg.locale`` field should match the database
locale (the ``--locale`` parameter of the ``initdb`` command): for an utf8
encoded database the proper value may be ``it_IT.utf8``.

The suggested configuration has the following effect:

- regular words are processed by the Italian dictionary;
- single parts of hyphenated words are processed the same way;
- if a word can't be found in the Italian dictionary, leave it unchanged;
- the whole groups of hyphenated words are ignored (none of them is in the
  dictionary)
- numbers, URLs, e-mail addresses, file paths are left unchanged.

To test if the configuration behaves properly, you can use the ``ts_debug``
functions, returning informations about the single tokens and how they
have been transformed::

    tstest=# SELECT tok_type, description, token, tsvector
    FROM ts_debug($$
    <p>Ma quell'ampolla non aveva l'iscrizione «Veleno». Quindi Alice
    si arrischiò a berne un sorso. Era una bevanda deliziosa (aveva
    un sapore misto di torta di ciliegie, di crema, d'ananasso,
    di gallinaccio arrosto, di torrone, e di crostini imburrati)
    e la tracannò d'un fiato.</p>
    $$);
     tok_type | description |    token    |     tsvector
    ----------+-------------+-------------+-------------------
     lword    | Latin word  | Ma          |
     lword    | Latin word  | quell       |
     lword    | Latin word  | ampolla     | 'ampolla'
     lword    | Latin word  | non         | 'non'
     lword    | Latin word  | aveva       |
     lword    | Latin word  | l           |
     lword    | Latin word  | iscrizione  | 'iscrizione'
     lword    | Latin word  | Veleno      | 'veleno'
     lword    | Latin word  | Quindi      |
     lword    | Latin word  | Alice       | 'alice'
     lword    | Latin word  | si          |
     word     | Word        | arrischiò   | 'arrischiare'
     lword    | Latin word  | a           |
     lword    | Latin word  | berne       | 'bere'
     lword    | Latin word  | un          |
     lword    | Latin word  | sorso       | 'sorso'
     lword    | Latin word  | Era         |
     lword    | Latin word  | una         |
     lword    | Latin word  | bevanda     | 'bevanda'
     lword    | Latin word  | deliziosa   | 'delizioso'
     lword    | Latin word  | aveva       |
     lword    | Latin word  | un          |
     lword    | Latin word  | sapore      | 'sapore'
     lword    | Latin word  | misto       | 'misto'
     lword    | Latin word  | di          |
     lword    | Latin word  | torta       | 'torta' 'torcere'
     lword    | Latin word  | di          |
     lword    | Latin word  | ciliegie    | 'ciliegio'
     lword    | Latin word  | di          |
     lword    | Latin word  | crema       | 'crema' 'cremare'
     lword    | Latin word  | d           |
     lword    | Latin word  | ananasso    | 'ananasso'
     lword    | Latin word  | di          |
     lword    | Latin word  | gallinaccio | 'gallinaccio'
     lword    | Latin word  | arrosto     | 'arrostare'
     lword    | Latin word  | di          |
     lword    | Latin word  | torrone     | 'torrone'
     lword    | Latin word  | e           |
     lword    | Latin word  | di          |
     lword    | Latin word  | crostini    | 'crostino'
     lword    | Latin word  | imburrati   | 'imburrare'
     lword    | Latin word  | e           |
     lword    | Latin word  | la          |
     word     | Word        | tracannò    | 'tracannare'
     lword    | Latin word  | d           |
     lword    | Latin word  | un          |
     lword    | Latin word  | fiato       | 'fiato' 'fiatare'
    (47 rows)


Using a *stemmer* as alternative dictionary
-------------------------------------------

With the suggested configuration, each word not recognized by the
Italian dictionary is passed to the ``simple`` dictionary, which leaves
them unchanged. A better choice may be the use of a *stemmer* as secondary
dictionary: the stemmer task is to remove the variable endings from the
words leaving only the root.

The stemmer may prove handy in many cases. For example to take into account the
basic variation of journalistic neologisms::

    tstest=# -- http://en.wiktionary.org/wiki/Cerchiobottista
    tstest=# UPDATE pg_ts_cfgmap
            SET dict_name = '{it_spell,it_stem}'
            WHERE ts_name = 'default_italian'
            AND tok_alias IN ('word', 'lword', 'nlword',
                'part_hword', 'lpart_hword', 'nlpart_hword');
    UPDATE 6
    tstest=# SELECT to_tsvector('Cerchiobottisti alla riscossa')
                @@ to_tsquery('cerchiobottismo');
     ?column?
    ----------
     t
    (1 row)

The Italian stemmer also has the property of leaving most of the English words
untouched (probably because English words mostly end with consonants while
the stemmer is tweaked to recognize typical Italian words suffixes, which
usually end with vowels), thus being usable for Italian texts peppered
with many English words (such as technical documentation) without
generating too many false positives.

You can install a stemmer following the documentation of the Gendict_ tool
and downloading stemming rules from the Snowball_ stemmer site (you should
use the version matching your database encoding).

.. _Gendict: http://www.sai.msu.su/~megera/postgres/gist/tsearch/V2/
                docs/README.gendict
.. _Snowball: http://snowball.tartarus.org/algorithms/italian/

You may found some difficulties in compiling the stemmer sources together with
Tsearch2: it seems that lately the two system interfaces have become
incompatible. You can find many informations online about `how to compile
Snowball with Tsearch2`__. Furthermore the `mailing list`__ is a warm and
comfortable place.

.. __: http://www.mail-archive.com/pgsql-general@postgresql.org/msg94518.html
.. __: https://lists.sourceforge.net/lists/listinfo/openfts-general


Acknowledgements
================

I wish to thank **Davide Prina** and **Gianluca Turconi**, because without
their `progetto linguistico`_ i wouldn't have had anything to work upon.

I also hearty thank **Oleg Bartunov** and **Teodor Sigaev**, the Tsearch2_
authors.

And many thanks to Develer_, one of the finest hackers assembly in Italy!

...and to my angel, patiently tolerating my jet lag.

.. _Develer: http://www.develer.com
