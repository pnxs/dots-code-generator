#!/usr/bin/env python3

from simpleparse.parser import Parser
from simpleparse.dispatchprocessor import *
import copy
#import pprint

ddlGrammar = r"""
file            := wsn, content
content         := directive*, wsn
directive       := !, (struct / enum / import_file / comment), wsn
import_file     := 'import', !, wsn, path
struct          := multiline_comment?, wsn, 'struct', !, wsn, name, wsn, options?, '{', wsn, attribute*, '}', wsn
attribute       := multiline_comment?, ws, tag, ":", ws, options?, (vector_type / type), ws, name, ws, ";", comment?, wsn
multiline_comment := comment+
comment         := ws, '//', !, ws, comment_text, nl
comment_text     := -'\n'*
option          := name, ("=", option_value)?
options         := "[", (option, ","?)+, "]", wsn
option_value     := [A-Za-z0-9_]+

enum            := multiline_comment?, 'enum', !, wsn, name, wsn, '{', wsn, enum_item*, '}', wsn
enum_item       := multiline_comment?, ws, tag, ":", wsn, name, (wsn, '=', wsn, value)?, wsn, [,]?, comment*, wsn

name            := identifier
type            := identifier
vector_type      := 'vector<', wsn, vector_type_name, wsn, '>'
vector_type_name  := identifier
tag             := [0-9]+
value           := [-0-9]+
path            := -'\n'*
<wsn>           := [ \t\n]*
<ws>            := [ \t]*
<nl>            := '\n'
<alpha>         := [A-Za-z]+
<identifier>    := [a-zA-Z], [a-zA-Z0-9_]*
"""

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

class DDLProcessor(DispatchProcessor):
    def __init__(self, config):
        self.imports = []
        self.structs = []
        self.enums = []
        self.vectorFormat = config["vector_format"]
        self.typeMapping = config["type_mapping"]

    def mappedType(self, attr):
        outputFormat = "{}"
        tn = attr["type"]
        if attr["vector"]:
            outputFormat = self.vectorFormat
            tn = attr["vector_type"]

        # Imported names will not be changed
        if tn in self.imports:
            return outputFormat.format(tn)

        if tn not in self.typeMapping:
            return outputFormat.format(tn)
            #raise Exception("Unknown type: '%s'" % tn)
        return outputFormat.format(self.typeMapping[tn])

    def struct(self, tup, in_buffer):
        tag, start, stop, childs = tup
        obj = {"attributes": [], "keys": [], "keyAttributes": [], "options": {}}

        for c in childs:
            cn = c[0]
            if cn == "multiline_comment":
                comment = dispatch(self, c, in_buffer)
                if ("structComment" not in obj):
                    obj["structComment"] = comment
                else:
                    obj["structComment"] += comment
            if cn == "attribute":
                d = dispatch(self, c, in_buffer)
                obj["attributes"].append(d)
                if d["key"]:
                    obj["keys"].append(d["name"])
                    obj["keyAttributes"].append(d)
            elif cn == "name":
                obj["name"] = dispatch(self, c, in_buffer)
            elif cn == "options":
                obj["options"] = dispatch(self, c, in_buffer)

        #pp = pprint.PrettyPrinter(depth=4)
        #print("Struct:")
        #pp.pprint(obj)
        self.structs.append(obj)

        return obj

    def enum(self, tup, in_buffer):
        tag, start, stop, childs = tup
        obj = {"items": []}
        for c in childs:
            cn = c[0]
            if cn == "name":
                obj["name"] = dispatch(self, c, in_buffer)
            elif cn == "enum_item":
                obj["items"].append(dispatch(self, c, in_buffer))
        obj["Name"] = obj["name"][0].upper() + obj["name"][1:]
        
        #pp = pprint.PrettyPrinter(depth=4)
        #print("Enum:")
        #pp.pprint(obj)

        self.enums.append(obj)
        return obj

    def enum_item(self, tup, in_buffer):
        tag, start, stop, childs = tup
        attr = singleMap(childs, self, in_buffer)

        if "value" not in attr:
            attr["value"] = attr["tag"] - 1
        attr["Name"] = attr["name"][0].upper() + attr["name"][1:]
        return attr

    def import_file(self, tup, in_buffer):
        tag, start, stop, childs = tup
        self.imports.append(dispatch(self, childs[0], in_buffer))

    def content(self, tup, in_buffer):
        tag, start, stop, childs = tup
        dispatchList(self, childs, in_buffer)
        return {'structs': self.structs, 'enums': self.enums, 'imports': self.imports}

    def directive(self, tup, in_buffer):
        tag, start, stop, childs = tup
        ret = []
        for c in childs:
            if c[0] == "comment":
                continue
            else:
                ret.append(dispatch(self, c, in_buffer))
        return ret

    @staticmethod
    def path(tup, in_buffer):
        return getString(tup, in_buffer)

    @staticmethod
    def tag(tup, in_buffer):
        return int(getString(tup, in_buffer))

    @staticmethod
    def value(tup, in_buffer):
        return int(getString(tup, in_buffer))

    @staticmethod
    def type(tup, in_buffer):
        return getString(tup, in_buffer)

    def vector_type(self, tup, in_buffer):
        tag, start, stop, childs = tup
        return dispatch(self, childs[0], in_buffer)

    @staticmethod
    def vector_type_name(tup, in_buffer):
        return getString(tup, in_buffer)

    @staticmethod
    def name(tup, in_buffer):
        return getString(tup, in_buffer)

    @staticmethod
    def option_value(tup, in_buffer):
        return getString(tup, in_buffer)

    def comment(self, tup, in_buffer):
        tag, start, stop, childs = tup
        for c in childs:
            if c[0] == "comment_text":
                return dispatch(self, c, in_buffer)

    def multiline_comment(self, tup, in_buffer):
        tag, start, stop, childs = tup
        comment_text = []
        for c in childs:
            if c[0] == "comment":
                comment_text.append(dispatch(self, c, in_buffer))
        return comment_text

    @staticmethod
    def comment_text(tup, in_buffer):
        return getString(tup, in_buffer)

    def attribute(self, tup, in_buffer):
        tag, start, stop, childs = tup
        attr = singleMap(childs, self, in_buffer)
        attr["key"] = False
        attr["vector"] = False

        if "options" in attr and "key" in attr["options"]:
            attr["key"] = attr["options"]["key"]

        if "vector_type" in attr:
            attr["type"] = "vector<%s>" % attr["vector_type"]
            attr["vector"] = True
            vectorAttr = copy.copy(attr)
            vectorAttr["vector"] = False
            vectorAttr["type"] = vectorAttr["vector_type"]
            attr["cxx_vector_type"] = self.mappedType(vectorAttr)

        attr["cxx_type"] = self.mappedType(attr)
        attr["Name"] = attr["name"][0].upper() + attr["name"][1:]

        return attr

    def option(self, tup, in_buffer):
        tag, start, stop, childs = tup
        return dispatchList(self, childs, in_buffer)

    def options(self, tup, in_buffer):
        tag, start, stop, childs = tup
        opts = {}
        for c in childs:
            if c[0] == "option":
                d = dispatch(self, c, in_buffer)
                if len(d) == 1:
                    opts[d[0]] = True
                else:
                    opts[d[0]] = d[1]
        return opts


class DdlParser(object):
    def __init__(self):
        self.scanner = Parser(ddlGrammar, 'file')
        self.ddlconfig = {
            "vector_format": "dots::Vector<%s>",
            "type_mapping": type_mapping_1_1
        }

    def parse(self, data):
        success, structs, next_char = self.scanner.parse(data, processor=DDLProcessor(self.ddlconfig))
        if not success:
            raise Exception("Parsing error")
        return structs[0]
