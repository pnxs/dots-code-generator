from . dots_parser import Transformer, v_args
import copy


class DotsTransformer(Transformer):
    def __init__(self, config):
        super(DotsTransformer, self).__init__()
        self.structs = []
        self.imports = []
        self.enums = []
        self.mapped_types = {}
        self.vectorFormat = config["vector_format"]
        self.typeMapping = config["type_mapping"]

        self.p_is_vector = False
        self.p_vector_type = None

    def _mapped_type(self, attr):
        output_format = "{}"
        tn = attr["type"]
        if attr["vector"]:
            output_format = self.vectorFormat
            tn = attr["vector_type"]

        # Imported names will not be changed
        if tn in self.imports:
            return output_format.format(tn)

        if tn not in self.typeMapping:
            return output_format.format(tn)
            #raise Exception("Unknown type: '%s'" % tn)
        return output_format.format(self.typeMapping[tn])

    def transform(self, tree):
        tree = super(DotsTransformer, self).transform(tree)
        return {
            'enums': self.enums,
            'structs': self.structs,
            'imports': self.imports
        }

    @v_args(inline=True)
    def option(self, name, value):
        if value is None:
            value = True
        return str(name), value

    def doc_comment(self, v):
        return str(v[0].strip("/ "))

    @v_args(inline=True)
    def type(self, v):
        return str(v)

    @v_args(inline=True)
    def property(self, doc_comment, tag, options, type_name, name, comment):
        is_key = False if not options else "key" in options
        is_vector = self.p_is_vector
        p = {
            "name": name,
            "Name": name[0].upper() + name[1:],
            "tag": int(tag),
            "type": type_name,
            "key": is_key,
            "vector": is_vector
        }
        if options:
            p["options"] = options
        if doc_comment:
            p["doc"] = doc_comment
        if comment:
            p["comment"] = comment
        if is_vector:
            p["vector_type"] = self.p_vector_type
            vector_property = copy.copy(p)
            vector_property["vector"] = False
            vector_property["type"] = vector_property["vector_type"]
            p["cxx_vector_type"] = self._mapped_type(vector_property)
        p["cxx_type"] = self._mapped_type(p)

        # Reset vector-members
        self.p_is_vector = False
        self.p_vector_type = None

        return p

    @v_args(inline=True)
    def vector_type(self, t):
        self.p_is_vector = True
        self.p_vector_type = t
        return f"vector<{t}>"

    @v_args(inline=True)
    def struct(self, doc_comment, struct_name, options, properties):
        key_properties = []
        keys = []

        for p in properties:
            if p["key"]:
                keys.append(p["name"])
                key_properties.append(p)

        s = {
            "name": struct_name,
            "options": options if options else {},
            "attributes": properties,
            "keyAttributes": key_properties,
            "keys": keys
        }
        if doc_comment:
            s["structComment"] = doc_comment

        self.structs.append(s)
        return s

    @v_args(inline=True)
    def enum_item(self, doc_comment, tag, enum_name, enum_value, comment):
        ei = {
            "tag": int(tag),
            "name": enum_name,
            "Name": enum_name[0].upper() + enum_name[1:],
            "value": enum_value if enum_value else int(tag)-1
        }
        if doc_comment:
            ei["doc"] = doc_comment
        if comment:
            ei["comment"] = comment
        return ei

    @v_args(inline=True)
    def enum(self, doc_comment, name, enum_items):
        e = {
            "name": name,
            "Name": name[0].upper() + name[1:],
            "items": enum_items
        }
        if doc_comment:
            e["doc"] = doc_comment
        self.enums.append(e)
        return e

    def import_(self, v):
        self.imports.append(str(v[0]))

    PROPERTY_NAME = str
    CNAME = str
    INT = int
    options = dict
    struct_properties = list
    enum_items = list
    doc_comments = list
    structs = list
    true = lambda self, _: True
    false = lambda self, _: False
