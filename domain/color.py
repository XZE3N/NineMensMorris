from enum import Enum


class Color(Enum):
    """
    Helper class to represent colors for the Nine Men's Morris pieces.
    """
    WHITE = 1
    BLACK = 2


class ANSIColors:
    """
    Return ANSI escape sequences to use colors in the console.
    """
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
