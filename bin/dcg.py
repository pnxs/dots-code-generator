#!/usr/bin/env python3

"""
Dots Code Generator
"""

from __future__ import print_function

import importlib
import sys
import filecmp
import os
import pathlib

from optparse import OptionParser
sys.path.insert(1, os.path.join(pathlib.Path(__file__).parent.absolute(), '..'))
from dots import DdlParser, DdlTemplate

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def str2bool(string):
    string = string.lower()
    if string == "true":
        return True
    elif string == "false":
        return False
    else:
        raise Exception("error converting '%s' to boolean" % string)

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
        return "ERROR in Type %s: Tag '%d' from property '%s' was previously used in property '%s'." % (self.typeName, self.tag, self.propertyName, self.previousPropertyName)


class DotsCodeGenerator:
    configFile           = None
    template_path         = "."
    output_path           = "."
    verbose              = False
    list_generated       = False
    defines              = {}

    struct_templates     = []
    enum_templates       = []
    type_mapping         = {}
    vector_format        = ""
    custom_filters       = {}

    default_options      = {
        "cached": True,
        "cleanup": False,
        "persistent": False,
        "internal": False,
        "local": False,
        "substruct_only": False
    }

    def load_config(self, config_file):
        config_file_path = pathlib.Path(config_file)
        if config_file_path.exists():
            sys.path.insert(1, str(config_file_path.parent))
            config_file = config_file_path.stem
        if self.verbose:
            print("Load config from file %s / %s %d" % (config_file_path, config_file, config_file_path.exists()))
        config = importlib.import_module(config_file)

        if config:
            self.struct_templates = config.struct_templates
            self.enum_templates = config.enum_templates
            self.type_mapping = config.type_mapping
            self.vector_format = config.vector_format
            if 'filters' in dir(config):
                self.custom_filters = config.filters
    

    @staticmethod
    def output_names(name, template_list):
        out_names = {}
        tn = name
        for template in template_list:
            # Strip .dotsT
            orig_template_name = template
            if template.endswith(".dotsT"):
                template = template[:-6]
            # Strip <template-name>
            template_ext = template[template.find("."):]
            out_names[orig_template_name] = "%s%s" % (tn, template_ext)
        return out_names

    @staticmethod
    def print_output_names(output_names):
        for key in output_names:
            on = output_names[key]
            print(on)

    def process_options(self, options):
        default_options = self.default_options.copy()
        for option in options:
            option_value = options[option]

            if option == "cached":
                if not type(option_value) is bool:
                    options[option] = str2bool(option_value)

            # Remove from default_options-dict when option was set
            if option in default_options:
                del default_options[option]

        # Set all default_options, that were not set before
        for option in default_options:
            options[option] = default_options[option]

    @staticmethod
    def is_file_equal(left, right):
        try:
            if not os.path.exists(left) or not os.path.exists(right):
                return False
            ret = filecmp.cmp(left, right, shallow=False)
            #eprint("Check ", left, right, ret)
            return ret
        except Exception as e:
            eprint("Exception:", e)
            return False

    def generate_file(self, file_name, key, fs):
        abs_file_name = self.output_path + "/" + file_name
        abs_temp_file_name = abs_file_name + ".tmp"

        jinja = DdlTemplate(self.template_path, abs_temp_file_name, self.custom_filters)
        jinja.render(key, fs)

        # Check if tempFileName is different to fileName, only overwrite if different
        if not self.is_file_equal(abs_temp_file_name, abs_file_name):
            eprint("created " + file_name)
            os.replace(abs_temp_file_name, abs_file_name)
        else:
            os.remove(abs_temp_file_name)


    def generate_enum(self, enum, s):
        fs = enum
        fs["imports"] = s["imports"]
        fs["includes"] = []
        fs["defines"] = self.defines
        fs["package"] = s["package"]

        output_names = self.output_names(enum["name"], self.enum_templates)

        if self.list_generated:
            self.print_output_names(output_names)
            return
        
        if self.verbose:
            eprint("  Enum %s" % enum["name"])
        
        for key in output_names:
            self.generate_file(output_names[key], key, fs)
    
    def generate_struct(self, struct, s):
        fs = struct
        fs["includes"] = []
        fs["defines"] = self.defines
        fs["package"] = s["package"]

        self.process_options(fs["options"])

        
        # Build list of self defined struct types
        struct_types = []
        for attr in struct["attributes"]:
            if attr["vector"]:
                t = attr["vector_type"]
            else:
                t = attr["type"]

            if t not in self.type_mapping:
                struct_types.append(t)

        # Filter any imports, that are not needed by this struct
        need_to_import = set(s["imports"]) & set(struct_types)
        # Add missing imports for struct
        need_to_import = need_to_import | set(struct_types)
        fs["imports"] = sorted(list(need_to_import))

        output_names = self.output_names(struct["name"], self.struct_templates)
        
        if self.list_generated:
            self.print_output_names(output_names)
            return
    
        if self.verbose:
            eprint("  Struct %s" % struct["name"])

        for key in output_names:
            self.generate_file(output_names[key], key, fs)


    def check_struct_unique_tags(self, struct):
        seen_properties = {}
        for attr in struct["attributes"]:
            tag = attr["tag"]
            if tag in seen_properties:
                raise NonUniqueTagError(attr["name"], tag, attr["name"], seen_properties[tag]["name"])
                print("ERROR in Type %s: Tag '%d' from property '%s' was previously used in property '%s'." % 
                        (attr["name"], tag, attr["name"], seen_properties[tag]["name"]))
            seen_properties[tag] = attr

    def check_consistency_enum(self, enums):
        pass

    def check_consistency_struct(self, struct):
        self.check_struct_unique_tags(struct)

    def process_file(self, file_name):
        if self.verbose:
            eprint("Process file " + file_name)
        fd = open(file_name, "r")

        #output_path = self.output_path
        #bn = os.path.basename(file_name)

        gen = DdlParser()
        gen.ddlconfig["vector_format"] = self.vector_format
        gen.ddlconfig["type_mapping"] = self.type_mapping
        s = gen.parse(fd.read())

        for enum in s["enums"]:
            self.check_consistency_enum(enum)
            self.generate_enum(enum, s)

        for struct in s["structs"]:
            self.check_consistency_struct(struct)
            self.generate_struct(struct, s)

    
if __name__ == "__main__":
    usage = "usage: %prog -C <config-file> [-D] [-T <template-path>] [-o <output-path>] [-v] [-M] <dots-files>"
    parser = OptionParser(usage=usage)
    parser.add_option("-C", "--config", dest="config_file")
    parser.add_option("-D", "--define", dest="define", action="append")
    parser.add_option("-T", "--templatePath", dest="template_path",
                    help="path to directory with template-files")
    parser.add_option("-o", "--outputPath", dest="output_path", default=".",
                    help="path of output files")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="verbose output")
    parser.add_option("-M", "--list-generated", dest="list_generated", action="store_true", default=False, help="list generated output files")

    (options, args) = parser.parse_args()

    dcg = DotsCodeGenerator()
    configFile = None
    if "DOTS_TEMPLATE_PATH" in os.environ:
        dcg.template_path = os.environ["DOTS_TEMPLATE_PATH"]
    if "DCG_CONFIG_FILE" in os.environ:
        configFile = os.environ["DCG_CONFIG_FILE"]
    if options.template_path is not None:
        dcg.template_path = options.template_path
    if options.config_file:
        configFile = options.config_file
    if options.list_generated:
        dcg.list_generated = options.list_generated
    if options.verbose:
        dcg.verbose = True
    if options.define:
        defines = {}
        for define in options.define:
            define, value = define.split("=", 1)
            defines[define] = value
        dcg.defines = defines
    dcg.output_path = options.output_path

    if configFile is None or len(configFile) == 0:
        parser.error("No config file given.")
    
    dcg.load_config(configFile)

    if dcg.verbose:
        eprint("Templatepath: '%s'" % options.template_path)
        eprint("Output generated:", options.list_generated)

    try:
        for file in args:
            dcg.process_file(file)

    except NonUniqueTagError as e:
        print(e)
        sys.exit(1)
