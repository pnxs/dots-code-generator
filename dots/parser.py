from . dots_parser import Lark_StandAlone
from . DotsTransformer import DotsTransformer

type_mapping_1_1 = {
    "bool": "bool",
    "int8": "int8",
    "int16": "int16",
    "int32": "int32",
    "int64": "int64",
    "uint8": "uint8",
    "uint16": "uint16",
    "uint32": "uint32",
    "uint64": "uint64",
    "float32": "float32",
    "float64": "float64",
    "float128": "float128",
    "duration": "duration",
    "time_point": "time_point",
    "steady_timepoint": "steady_timepoint",
    "string": "string",
    "property_set": "property_set"
}


class DdlParser(object):
    def __init__(self):
        self.parser = Lark_StandAlone()

        self.ddlconfig = {
            "vector_format": "dots::Vector<%s>",
            "type_mapping": type_mapping_1_1
        }

    def parse(self, data):
        tree = self.parser.parse(data)
        tree = DotsTransformer(self.ddlconfig).transform(tree)
        return tree
