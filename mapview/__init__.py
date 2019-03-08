# coding=utf-8
"""
MapView
=======

.. author:: Mathieu Virbel <mat@kivy.org>

MapView is a Kivy widget that display maps.
"""

__all__ = []
__version__ = "0.2"

import os
MIN_LATITUDE = -90.
MAX_LATITUDE = 90.
MIN_LONGITUDE = -180.
MAX_LONGITUDE = 180.
CACHE_DIR = os.environ.get('CACHE_DIR', "cache")

try:
    # fix if used within garden
    import sys
    sys.modules['mapview'] = sys.modules['kivy.garden.mapview.mapview']
    del sys
except KeyError:
    pass
