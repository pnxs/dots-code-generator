from . dots_parser import Transformer, v_args


class DotsTransformer(Transformer):
    def __init__(self, config):
        super(Transformer, self).__init__()
        self.structs = []
        self.imports = []
        self.package_ = None
        self.enums = []
        self.mapped_types = {}
        self.vectorFormat = config["vector_format"]
        self.instanceRefFormat = config.get("instance_ref_format", "instance_ref<{}>")
        self.typeMapping = config["type_mapping"]

    def _mapped_type(self, tn):
        if tn.startswith("vector<"):
            return self.vectorFormat.format(self._mapped_type(tn[7:-1]))
        if tn.startswith("instance_ref<"):
            return self.instanceRefFormat.format(tn[13:-1])
        # Imported names will not be changed
        if tn in self.imports:
            return tn
        return self.typeMapping.get(tn, tn)

    def transform(self, tree):
        tree = super(DotsTransformer, self).transform(tree)
        # Imported/externally defined names are resolved by the target compiler.
        # Check locally known targets after visiting all declarations so forward
        # references work as well as references to earlier declarations.
        from .parser import type_mapping_1_1
        non_struct_types = set(type_mapping_1_1) | {
            "any", "bytes", "uuid", "timepoint", "float16", "vector"
        } | {enum["name"] for enum in self.enums}
        for struct in self.structs:
            for attr in struct["attributes"]:
                tn = attr["type"]
                while tn.startswith("vector<"):
                    tn = tn[7:-1]
                if tn.startswith("instance_ref<") and tn[13:-1] in non_struct_types:
                    raise ValueError("instance_ref target must be a struct type: " + tn[13:-1])
        return {
            'enums': self.enums,
            'structs': self.structs,
            'imports': self.imports,
            'package': self.package_
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
        is_vector = type_name.startswith("vector<")
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
            p["vector_type"] = type_name[7:-1]
            p["cxx_vector_type"] = self._mapped_type(p["vector_type"])
        p["cxx_type"] = self._mapped_type(type_name)

        return p

    @v_args(inline=True)
    def vector_type(self, t):
        return f"vector<{t}>"

    @v_args(inline=True)
    def instance_ref_type(self, target):
        return "instance_ref" if target is None else f"instance_ref<{target}>"

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

    def package(self, v):
        self.package_ = str(v[0])

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
