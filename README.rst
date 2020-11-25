===================================
Italian Full-Text Search Dictionary
===================================

:Author: Daniele Varrazzo
:Contact: daniele.varrazzo@gmail.com
:Organization: `Develer S.r.l. <http://www.develer.com>`__
:Source code: https://github.com/dvarrazzo/italian_fts/

:Abstract: This package provides an ISpell dictionary to perform high quality
    *full text search* in Italian documents using the PostgreSQL_ database.

    Using the provided dictionary, search operations in Italian documents can
    keep into account morphological variations of Italian words, such as verb
    conjugations.

    .. _PostgreSQL: http://www.postgresql.org
    .. _Tsearch2: http://www.sai.msu.su/~megera/postgres/gist/tsearch/V2/


:Copyright: 2001, 2002 Gianluca Turconi
:Copyright: 2002, 2003, 2004 Gianluca Turconi and Davide Prina
:Copyright: 2004, 2005, 2006 Davide Prina
:Copyright: 2007-2020 Daniele Varrazzo


Package description
===================

This package contains an ISpell dictionary useful to perform high quality
full-text searches in Italian language documents. The package also contains
installation and configuration files.


Prerequisites
=============

This package can be used to install and configure the ISpell dictionary in
all supported PostgreSQL versions.


Package installation
====================

You can use the `PGXN Client`__ to install the dictionary::

    $ [sudo] pgxn install italian_fts

.. __: https://pgxn.github.io/pgxnclient/

This installs the extension files in the PostgreSQL cluster. Please check
`pgxn install`__ options if you have more than one cluster.

.. __: https://pgxn.github.io/pgxnclient/usage.html#pgxn-install

After the package has been installed you can use SQL command `CREATE
EXTENSION`__ to make the dictionary available in a database::

    CREATE EXTENSION italian_fts;

.. __: https://www.postgresql.org/docs/current/sql-createextension.html


Dictionary usage
================

The extension creates a text search dictionary ``italian_ispell`` and a text
search configuration also called ``italian_ispell`` using the dictionary as a
default and falling back to the Snowball stemmer ``italian_stem`` (installed
by default by PostgreSQL) when a word is not found.  Here is a result of the
process of a sample text with the ``italian_ispell`` configuration::

    =# select token, dictionary, lexemes
        from ts_debug('italian_ispell', $$
            Né più mai toccherò le sacre sponde
            ove il mio corpo fanciulletto giacque,
            Zacinto mia, che te specchi nell'onde
            del greco mar da cui vergine nacque
            ...
        $$)
        where array_upper(lexemes,1) <> 0;

        token     |   dictionary   |    lexemes
    --------------+----------------+----------------
     più          | italian_ispell | {più}
     mai          | italian_ispell | {mai}
     toccherò     | italian_ispell | {toccare}
     sacre        | italian_ispell | {sacro}
     sponde       | italian_ispell | {sponda}
     ove          | italian_ispell | {ove}
     corpo        | italian_ispell | {corpo}
     fanciulletto | italian_ispell | {fanciulletto}
     giacque      | italian_ispell | {giacere}
     Zacinto      | italian_stem   | {zacint}
     specchi      | italian_ispell | {specchiare}
     onde         | italian_ispell | {onda}
     greco        | italian_ispell | {greco}
     mar          | italian_ispell | {mare}
     vergine      | italian_ispell | {vergine}
     nacque       | italian_ispell | {nascere}
    (16 rows)

For general usage of the full-text search features in PostgreSQL please refer
to the `database documentation`__.

.. __: https://www.postgresql.org/docs/current/textsearch.html

