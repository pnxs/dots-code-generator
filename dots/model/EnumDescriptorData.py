from dots.model.EnumElementDescriptor import EnumElementDescriptor

class EnumDescriptorData:
    __dots_object__ = True
    __dots_attributes__ = {
        1: {"key": True, "dots_type": "string", "name": "name", "class": str},
        2: {"key": False, "dots_type": "vector<EnumElementDescriptor>", "name": "elements", "class": list, "list_type": EnumElementDescriptor},
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
        self.elements = None  # type: list
