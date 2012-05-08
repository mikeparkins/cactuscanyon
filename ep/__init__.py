__all__ = [
    'ep_layers',
    'ep_transition'
]
from ep_layers import *
from ep_transition import *

import locale

# Used to put commas in the score.
locale.setlocale(locale.LC_ALL, "")


DMD_PATH = "dmd/"
LAMPSHOWS_PATH = "lampshows/"
SOUNDS_PATH = "sounds/"
SFX_PATH = "sounds/sfx/"
MUSIC_PATH = "sounds/music/"
QUOTES_PATH = "sounds/quotes/"

def format_score(score):
    """Returns a string representation of the given score value.
         Override to customize the display of numeric score values."""
    if score == 0:
        return '00'
    else:
        return locale.format("%d", score, True)