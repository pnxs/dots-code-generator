from typing import List
from datetime import datetime

from dots.model.DotsStructFlags import DotsStructFlags
from dots.model.StructDocumentation import StructDocumentation
from dots.model.StructPropertyData import StructPropertyData
from dots.model.DotsStructScope import DotsStructScope

class StructDescriptorData:
    __dots_object__ = True
    __dots_attributes__ = {
        1: {"key": True, "dots_type": "string", "name": "name", "class": str},
        2: {"key": False, "dots_type": "vector<StructPropertyData>", "name": "properties", "class": list, "list_type": StructPropertyData},
        3: {"key": False, "dots_type": "StructDocumentation", "name": "documentation", "class": StructDocumentation},
        4: {"key": False, "dots_type": "DotsStructScope", "name": "scope", "class": DotsStructScope},
        5: {"key": False, "dots_type": "DotsStructFlags", "name": "flags", "class": DotsStructFlags},
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
        self.properties = None  # type: list
        self.documentation = None  # type: StructDocumentation
        self.scope = None  # type: DotsStructScope
        self.flags = None  # type: DotsStructFlags
