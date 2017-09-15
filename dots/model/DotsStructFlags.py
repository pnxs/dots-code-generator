from typing import List
from datetime import datetime


class DotsStructFlags:
    __dots_object__ = True
    __dots_attributes__ = {
        1: {"key": False, "dots_type": "bool", "name": "cached", "class": bool},
        2: {"key": False, "dots_type": "bool", "name": "internal", "class": bool},
        3: {"key": False, "dots_type": "bool", "name": "persistent", "class": bool},
        4: {"key": False, "dots_type": "bool", "name": "cleanup", "class": bool},
        5: {"key": False, "dots_type": "bool", "name": "local", "class": bool},
        6: {"key": False, "dots_type": "bool", "name": "substructOnly", "class": bool},
    }

    _dots_options = {
        "cleanup": False,
        "cached": False,
        "substruct_only": False,
        "internal": True,
        "local": False,
        "persistent": False,
    }

    def __init__(self):
        self.cached = None  # type: bool
        self.internal = None  # type: bool
        self.persistent = None  # type: bool
        self.cleanup = None  # type: bool
        self.local = None  # type: bool
        self.substructOnly = None  # type: bool
