"""
Constants to be used by my_browser
"""

from enum import Enum


class Schemes(Enum):
    """
    Valid Schemes
    """
    FILE = "file"
    HTTPS = "https"
    HTTP = "http"
    DATA = "data"
