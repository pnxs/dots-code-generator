#!/usr/bin/env python3

"""
Dots Code Generator
"""

from __future__ import print_function

import sys
import filecmp
import functools
import itertools
import operator
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
    
    def __init__(self, typeName, tagId, propertyName, previousPropertyName):
        self.typeName = typeName
        self.tag = tagId
        self.propertyName = propertyName
        self.previousPropertyName = previousPropertyName

    def __str__(self):
        return "ERROR in Type %s: Tag '%d' from property '%s' was previously used in property '%s'." % (self.typeName, self.tag, self.propertyName, self.previousPropertyName)


class DotsCodeGenerator:
    configFile           = None
    templatePath         = "."
    outputPath           = "."
    verbose              = False
    list_generated       = False
    defines              = {}

    struct_templates     = []
    enum_templates       = []
    type_mapping         = {}
    vector_format        = ""

    default_options      = {
        "cached": True,
        "cleanup": False,
        "persistent": False,
        "internal": False,
        "local": False,
        "substruct_only": False
    }

    def loadConfig(self, configFile):
        if self.verbose:
            eprint("Load config from file %s" % configFile)
        config_file_path = pathlib.Path(configFile)
        if config_file_path.exists():
            sys.path.insert(1, str(config_file_path.parent))
            configFile = config_file_path.stem
        config = __import__(configFile)

        if config:
            self.struct_templates = config.struct_templates
            self.enum_templates = config.enum_templates
            self.type_mapping = config.type_mapping
            self.vector_format = config.vector_format
    

    def outputNames(self, name, templateList):
        outNames = {}
        tn = name
        for template in templateList:
            # Strip .dotsT
            origTemplateName = template
            if template.endswith(".dotsT"):
                template = template[:-6]
            # Strip <template-name>
            templateExt = template[template.find("."):]
            outNames[origTemplateName] = "%s%s" % (tn, templateExt)
        return outNames

    def printOutputNames(self, outputNames):
        for key in outputNames:
            on = outputNames[key]
            print(on)

    def processOptions(self, options):
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

    def isFileEqual(self, left, right):
        try:
            if not os.path.exists(left) or not os.path.exists(right):
                return False
            ret = filecmp.cmp(left, right, shallow=False)
            #eprint("Check ", left, right, ret)
            return ret
        except Exception as e:
            eprint("Exception:", e)
            return False

    def generateFile(self, fileName, key, fs):
        absFileName = self.outputPath + "/" + fileName
        absTempFileName = absFileName + ".tmp"

        jinja = DdlTemplate(self.templatePath, absTempFileName)
        jinja.render(key, fs)

        # Check if tempFileName is different to fileName, only overwrite if different
        if not self.isFileEqual(absTempFileName, absFileName):
            eprint("created " + fileName)
            os.replace(absTempFileName, absFileName)
        else:
            os.remove(absTempFileName)


    def generateEnum(self, enum, s):
        fs = enum
        fs["imports"] = s["imports"]
        fs["includes"] = []
        fs["defines"] = self.defines

        outputNames = self.outputNames(enum["name"], self.enum_templates)

        if self.list_generated:
            self.printOutputNames(outputNames)
            return
        
        if self.verbose:
            eprint("  Enum %s" % enum["name"])
        
        for key in outputNames:
            self.generateFile(outputNames[key], key, fs)
    
    def generateStruct(self, struct, s):
        fs = struct
        fs["includes"] = []
        fs["defines"] = self.defines

        self.processOptions(fs["options"])

        
        # Build list of self defined struct types
        structTypes = []
        for attr in struct["attributes"]:
            t = None
            if attr["vector"]:
                t = attr["vector_type"]
            else:
                t = attr["type"]

            if t not in self.type_mapping:
                structTypes.append(t)

        # Filter any imports, that are not needed by this struct
        needToImport = set(s["imports"]) & set(structTypes)
        # Add missing imports for struct
        needToImport = needToImport | set(structTypes)
        fs["imports"] = sorted(list(needToImport))

        outputNames = self.outputNames(struct["name"], self.struct_templates)
        
        if self.list_generated:
            self.printOutputNames(outputNames)
            return
    
        if self.verbose:
            eprint("  Struct %s" % struct["name"])

        for key in outputNames:
            self.generateFile(outputNames[key], key, fs)


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

    def processFile(self, fileName):
        if self.verbose:
            eprint("Process file " + fileName)
        fd = open(fileName, "r")

        outputPath = self.outputPath

        bn = os.path.basename(fileName)

        gen = DdlParser()
        gen.ddlconfig["vector_format"] = self.vector_format
        gen.ddlconfig["type_mapping"] = self.type_mapping
        s = gen.parse(fd.read())

        for enum in s["enums"]:
            self.check_consistency_enum(enum)
            self.generateEnum(enum, s)

        for struct in s["structs"]:
            self.check_consistency_struct(struct)
            self.generateStruct(struct, s)

    
if __name__ == "__main__":
    usage = "usage: %prog -C <config-file> [-D] [-T <template-path>] [-o <output-path>] [-v] [-M] <dots-files>"
    parser = OptionParser(usage=usage)
    parser.add_option("-C", "--config", dest="configFile")
    parser.add_option("-D", "--define", dest="define", action="append")
    parser.add_option("-T", "--templatePath", dest="templatePath",
                    help="path to directory with template-files")
    parser.add_option("-o", "--outputPath", dest="outputPath", default=".",
                    help="path of output files")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="verbose output")
    parser.add_option("-M", "--list-generated", dest="list_generated", action="store_true", default=False, help="list generated output files")

    (options, args) = parser.parse_args()

    dcg = DotsCodeGenerator()
    configFile = None
    if "DOTS_TEMPLATE_PATH" in os.environ:
        dcg.templatePath = os.environ["DOTS_TEMPLATE_PATH"]
    if "DCG_CONFIG_FILE" in os.environ:
        configFile = os.environ["DCG_CONFIG_FILE"]
    if options.templatePath is not None:
        dcg.templatePath = options.templatePath
    if options.configFile:
        configFile = options.configFile
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
    dcg.outputPath = options.outputPath

    if configFile is None or len(configFile) == 0:
        parser.error("No config file given.")
    
    dcg.loadConfig(configFile)

    if dcg.verbose:
        eprint("Templatepath: '%s'" % options.templatePath)
        eprint("Output generated:", options.list_generated)

    try:
        for file in args:
            dcg.processFile(file)

    except NonUniqueTagError as e:
        print(e)
        sys.exit(1)
    
        
