==============================================
Dizionario per la Ricerca di Testo in Italiano
==============================================

:Autore: Daniele Varrazzo
:Contatto: piro (alla) develer.com
:Organizzazione: `Develer S.r.l. <http://www.develer.com>`__

:Riassunto: Questo package fornisce un dizionario ISpell per effettuare
    ricerche *full-text* di alta qualità in documenti in italiano utilizzando
    il database PostgreSQL_.

    La ricerca tiene in considerazione le variazioni caratteristiche della
    lingua italiana per restituire i documenti corrispondenti ai criteri di
    ricerca, ad esempio le diverse coniugazioni verbali.

    .. _PostgreSQL: http://www.postgresql.org
    .. _Tsearch2: http://www.sai.msu.su/~megera/postgres/gist/tsearch/V2/


:Copyright: 2001, 2002 Gianluca Turconi
:Copyright: 2002, 2003, 2004 Gianluca Turconi and Davide Prina
:Copyright: 2004, 2005, 2006 Davide Prina
:Copyright: 2007-2011 Daniele Varrazzo


Informazioni sul pacchetto
==========================

Questo pacchetto contiene il dizionario ISpell per effettuare ricerche
full-text di buona qualità su documenti in lingua italiana. Il pacchetto
include anche i file di installazione e configurazione del dizionario.


Prerequisiti
============

Il pacchetto è adatto all'installazione in database PostgreSQL versione 8.3 e
successive.


Installazione del pacchetto
===========================

Usa il comando::

    sudo make install

per installare i file del dizionario nelle directory di destinazione. Questo
comando utilizza il primo ``pg_config`` trovato nel ``PATH`` per leggere la
configurazione del database.  Se vuoi specificare un diverso database puoi
usare la variabile ``PG_CONFIG`` per indicare un diverso programma::

    sudo make PG_CONFIG=/path/to/pg_config install


Per installare il dizionario in un database PostgreSQL con versione precedente
alla 9.1 puoi utilizzare il comando:

.. parsed-literal::

    psql -f $(pg_config --sharedir)/italian_fts/italian_fts.sql *nomedb*

La stessa directory contiene anche un file di disinstallazione.

In PostgreSQL 9.1 invece puoi usare i `comandi di gestione delle estensioni`__
per installare il dizionario::

    CREATE EXTENSION italian_fts;

.. __: http://developer.postgresql.org/pgdocs/postgres/extend-extensions.html
