-- italian_fts -- installation script
--
-- Copyright (C) 2007-2011 Daniele Varrazzo


CREATE TEXT SEARCH DICTIONARY italian_ispell (
    TEMPLATE = ispell,
    DictFile = italian_ispell,
    AffFile = italian_ispell,
    StopWords = italian_ispell);

COMMENT ON TEXT SEARCH DICTIONARY italian_ispell
    IS 'ISpell dictionary for Italian language';


CREATE TEXT SEARCH CONFIGURATION italian_ispell (
    COPY = italian);

COMMENT ON TEXT SEARCH CONFIGURATION italian_ispell
    IS 'Configuration for Italian language with spelling dictionary';

ALTER TEXT SEARCH CONFIGURATION italian_ispell
    ALTER MAPPING FOR
        asciihword, asciiword, hword, hword_asciipart, hword_part, word
    WITH italian_ispell, italian_stem;

