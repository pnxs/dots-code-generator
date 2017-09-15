from typing import List
from datetime import datetime


class StructPropertyData:
    __dots_object__ = True
    __dots_attributes__ = {
        1: {"key": False, "dots_type": "string", "name": "name", "class": str},
        2: {"key": False, "dots_type": "uint32", "name": "tag", "class": int},
        3: {"key": False, "dots_type": "bool", "name": "isKey", "class": bool},
        4: {"key": False, "dots_type": "string", "name": "type", "class": str},
        5: {"key": False, "dots_type": "uint32", "name": "typeId", "class": int},
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
        self.name = None  # type: str
        self.tag = None  # type: int
        self.isKey = None  # type: bool
        self.type = None  # type: str
        self.typeId = None  # type: int
