#!/usr/bin/env python

from simpleparse.parser import Parser
from simpleparse.dispatchprocessor import *

ddlGrammar = r"""
file            := ws, content
content         := directive+, ws
directive       := (comment / import_file / struct / enum), ws
import_file     := 'import', ws, path
struct          := 'struct', ws, name, ws, options?, '{', ws, comment*, ws, attribute*, '}', ws
attribute       := tag, ":", ws, options?, (vector_type / type), ws, name, ws, ";", comment*, ws
comment         := ws, '//', ws, comment_text
comment_text     := -'\n'*
option          := name, ("=", option_value)?
options         := "[", (option, ","?)+, "]", ws
option_value     := [A-Za-z0-9_]+

enum            := 'enum', ws, name, ws, '{', ws, comment*, ws, enum_item*, '}', ws
enum_item       := tag, ":", ws, name, (ws, '=', ws, value)?, ws, [,]?, comment*, ws

name            := identifier
type            := identifier
vector_type      := 'vector<', ws, vector_type_name, ws, '>'
vector_type_name  := identifier
tag             := [0-9]+
value           := [-0-9]+
path            := -'\n'*
<ws>            := [ \t\n]*
<alpha>         := [A-Za-z]+
<identifier>    := [a-zA-Z], [a-zA-Z0-9_]*
"""


class DDLProcessor(DispatchProcessor):
    def __init__(self):
        self.imports = []
        self.structs = []
        self.enums = []

    def struct(self, tup, in_buffer):
        tag, start, stop, childs = tup
        obj = {"attributes": [], "keys": [], "keyAttributes": [], "options": {}}

        for c in childs:
            cn = c[0]
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
            elif cn == "comment":
                obj["structComment"] = dispatch(self, c, in_buffer)

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

        self.enums.append(obj)
        return obj

    def enum_item(self, tup, in_buffer):
        tag, start, stop, childs = tup
        attr = singleMap(childs, self, in_buffer)

        if "value" not in attr:
            attr["value"] = attr["tag"] - 1
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
            attr["type"] = "dots::Vector<" + attr["vector_type"] + ">"
            attr["vector"] = True

        attr["cxx_type"] = attr["type"]
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

    def parse(self, data):
        success, structs, next_char = self.scanner.parse(data, processor=DDLProcessor())
        if not success:
            raise Exception("Parsing error")
        return structs[0]
