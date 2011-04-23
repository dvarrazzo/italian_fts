--
--  Test italian_fts configuration
--

select token, dictionary, lexemes
from ts_debug('italian_ispell', $$
    Né più mai toccherò le sacre sponde
    ove il mio corpo fanciulletto giacque,
    Zacinto mia, che te specchi nell'onde
    del greco mar da cui vergine nacque
    ...
$$)
where array_upper(lexemes,1) <> 0;
