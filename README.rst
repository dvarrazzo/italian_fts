===================================
Italian Full-Text Search Dictionary
===================================

:Author: Daniele Varrazzo
:Contact: piro (at) develer.com
:Organization: `Develer S.r.l. <http://www.develer.com>`__

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
:Copyright: 2007-2011 Daniele Varrazzo


Package description
===================

This package contains an ISpell dictionary useful to perfrom high quality
full-text searches in Italian language documents. The package also contains
installation and configuration files.


Prerequisites
=============

This package can be used to install and configure the ISpell dictionary in
PostgreSQL 8.3 and later.


Package installation
====================

Use the command::

    sudo make install

to install the dictionary files in the target directories. The command will
use the first ``pg_config`` found on the ``PATH`` to read the database
configuration: to install the dictionary in a different database you can use
the ``PG_CONFIG`` variable::

    sudo make PG_CONFIG=/path/to/pg_config install

With PostgreSQL versions older than 9.1 you can install the dictionary in a
database with the command:

.. parsed-literal::

    psql -f $(pg_config --sharedir)/italian_fts/italian_fts.sql *dbname*

The same directory also contains an uninstall script.

With PostgreSQL 9.1 you can use the `extensions management commands`__ to
install the dictionary::

    CREATE EXTENSION italian_fts;

.. __: http://developer.postgresql.org/pgdocs/postgres/extend-extensions.html

