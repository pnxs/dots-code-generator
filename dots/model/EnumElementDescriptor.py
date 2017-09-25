
class EnumElementDescriptor:
    __dots_object__ = True
    __dots_attributes__ = {
        1: {"key": False, "dots_type": "int32", "name": "enum_value", "class": int},
        2: {"key": False, "dots_type": "string", "name": "name", "class": str},
        3: {"key": False, "dots_type": "uint32", "name": "tag", "class": int},
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
        self.enum_value = None  # type: int
        self.name = None  # type: str
        self.tag = None  # type: int
