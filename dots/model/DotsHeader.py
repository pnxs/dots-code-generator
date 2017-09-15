from typing import List
from datetime import datetime


class DotsHeader:
    __dots_object__ = True
    __dots_attributes__ = {
        1: {"key": False, "dots_type": "string", "name": "typeName", "class": str},
        2: {"key": False, "dots_type": "timepoint", "name": "sentTime", "class": datetime},
        7: {"key": False, "dots_type": "timepoint", "name": "serverSentTime", "class": datetime},
        3: {"key": False, "dots_type": "property_set", "name": "attributes", "class": int},
        4: {"key": False, "dots_type": "bool", "name": "removeObj", "class": bool},
        5: {"key": False, "dots_type": "uint32", "name": "sender", "class": int},
        6: {"key": False, "dots_type": "bool", "name": "isFromMyself", "class": bool},
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
        self.typeName = None  # type: str
        self.sentTime = None  # type: datetime
        self.serverSentTime = None  # type: datetime
        self.attributes = None  # type: int
        self.removeObj = None  # type: bool
        self.sender = None  # type: int
        self.isFromMyself = None  # type: bool
