from typing import List
from datetime import datetime


class StructDocumentation:
    __dots_object__ = True
    __dots_attributes__ = {
        1: {"key": False, "dots_type": "string", "name": "description", "class": str},
        2: {"key": False, "dots_type": "string", "name": "comment", "class": str},
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
        self.description = None  # type: str
        self.comment = None  # type: str
