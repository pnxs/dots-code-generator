from dots import DdlParser
from dots.model import StructDescriptorData, \
    StructPropertyData, EnumDescriptorData,\
    EnumElementDescriptor, DotsStructScope, \
    DotsStructFlags
import logging


class ParsingError(Exception):
    """Base class for parsing errors"""
    pass


class NonUniqueTagError(ParsingError):
    """Exception raised when a struct has non-unique tags"""

    def __init__(self, type_name, tag_id, property_name, previous_property_name):
        self.typeName = type_name
        self.tag = tag_id
        self.propertyName = property_name
        self.previousPropertyName = previous_property_name

    def __str__(self):
        return "ERROR in Type %s: Tag '%d' from property '%s' was previously used in property '%s'." % (
                self.typeName, self.tag, self.propertyName, self.previousPropertyName)


class BaseTypeDescriptor:
    def __init__(self, name):
        self.name = name


class TypeRegistry:
    def __init__(self):
        self.types = {}
        self.register_base_types()

    def register_base_types(self):
        self.types["int8"] = BaseTypeDescriptor("int8")
        self.types["int16"] = BaseTypeDescriptor("int16")
        self.types["int32"] = BaseTypeDescriptor("int32")
        self.types["int64"] = BaseTypeDescriptor("int64")

        self.types["uint8"] = BaseTypeDescriptor("uint8")
        self.types["uint16"] = BaseTypeDescriptor("uint16")
        self.types["uint32"] = BaseTypeDescriptor("uint32")
        self.types["uint64"] = BaseTypeDescriptor("uint64")

        self.types["float32"] = BaseTypeDescriptor("float32")
        self.types["float64"] = BaseTypeDescriptor("float64")
        self.types["float128"] = BaseTypeDescriptor("float128")

        self.types["string"] = BaseTypeDescriptor("string")
        self.types["duration"] = BaseTypeDescriptor("duration")
        self.types["timepoint"] = BaseTypeDescriptor("timepoint")
        self.types["steady_timepoint"] = BaseTypeDescriptor("steady_timepoint")
        self.types["uuid"] = BaseTypeDescriptor("uuid")

        self.types["property_set"] = BaseTypeDescriptor("property_set")

    def get_user_types(self):
        user_types = {}
        for t in self.types:
            if not isinstance(self.types[t], BaseTypeDescriptor):
                user_types[t] = self.types[t]

        return user_types

    def add_type(self, descriptor):
        if isinstance(descriptor, EnumDescriptorData):
            self.types[descriptor.name] = descriptor
        elif isinstance(descriptor, StructDescriptorData):
            self.types[descriptor.name] = descriptor
        else:
            raise Exception("try to add non-descriptor object to type_registry")

    def get_unresolved_types(self):
        unresolved = {}
        for t in self.types:
            desc = self.types[t]
            if isinstance(desc, StructDescriptorData):
                missing = []
                for property in desc.properties:
                    if property.type not in self.types:
                        missing.append(property.type)
                if len(missing) != 0:
                    unresolved[desc.name] = missing

        return unresolved


class DotsCodeGenerator:
    def __init__(self):
        self.type_registry = TypeRegistry()

    def check_struct_unique_tags(self, struct):
        seen_properties = {}
        for attr in struct["attributes"]:
            tag = attr["tag"]
            if tag in seen_properties:
                raise NonUniqueTagError(attr["name"], tag, attr["name"], seen_properties[tag]["name"])
            seen_properties[tag] = attr

    def check_consistency_enum(self, enums):
        pass

    def check_consistency_struct(self, struct):
        self.check_struct_unique_tags(struct)

    def createEnumDescriptor(self, enum):
        ed = EnumDescriptorData()

        ed.name = enum["name"]

        ed.elements = []

        for element in enum["items"]:
            ee = EnumElementDescriptor()
            ee.enum_value = element["value"]
            ee.name = element["name"]
            ee.tag = element["tag"]

            ed.elements.append(ee)

        logging.info("add enum-descriptor " + ed.name)

        return ed

    def createStructDescriptor(self, struct):
        sd = StructDescriptorData()

        sd.name = struct["name"]
        sd.properties = []

        for property in struct["attributes"]:
            sp = StructPropertyData()
            sp.name = property["name"]
            sp.tag = property["tag"]
            sp.type = property["type"]
            sp.isKey = property["key"]

            sd.properties.append(sp)

        sd.scope = DotsStructScope.GLOBAL
        sd.flags = DotsStructFlags()

        opt = struct["options"]

        sd.flags.cleanup = False
        sd.flags.cached = True
        sd.flags.internal = False
        sd.flags.persistent = False
        sd.flags.local = False
        sd.flags.substructOnly = False

        if "cleanup" in opt:
            sd.flags.cleanup = opt["cleanup"]
        if "cached" in opt:
            sd.flags.cached = opt["cached"]
        if "internal" in opt:
            sd.flags.internal = opt["internal"]
        if "persistent" in opt:
            sd.flags.persistent = opt["persistent"]
        if "local" in opt:
            sd.flags.local = opt["local"]
        if "substruct_only" in opt:
            sd.flags.substructOnly = opt["substruct_only"]

        return sd

    def read_input_file(self, file):
        logging.info("read DOTS-file " + file)
        fd = open(file, "r")

        gen = DdlParser()
        s = gen.parse(fd.read())

        for enum in s["enums"]:
            self.check_consistency_enum(enum)
            desc = self.createEnumDescriptor(enum)
            self.type_registry.add_type(desc)

        for struct in s["structs"]:
            self.check_consistency_struct(struct)
            desc = self.createStructDescriptor(struct)
            self.type_registry.add_type(desc)

    def read_input_files(self, files):
        for file in files:
            self.read_input_file(file)
