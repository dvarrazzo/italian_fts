SET search_path = public;
BEGIN;

CREATE TEXT SEARCH DICTIONARY italian_ispell (
    TEMPLATE = ispell,
    DictFile = italian,
    AffFile = italian,
    StopWords = italian_ispell);

ALTER TEXT SEARCH CONFIGURATION italian
    ALTER MAPPING FOR
        asciihword, asciiword, hword, hword_asciipart, hword_part, word
    WITH italian_ispell, italian_stem;

COMMIT;
