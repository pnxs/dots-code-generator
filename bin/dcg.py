#!/usr/bin/env python

"""
Dots Code Generator
"""

from __future__ import print_function
from optparse import OptionParser
from dots import DdlParser, DdlTemplate
import os

import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class DotsCodeGenerator:
    configFile           = None
    templatePath         = "."
    outputPath           = "."
    verbose              = False
    list_generated       = False

    struct_templates     = ("struct.dots.h.dotsT", "struct.dots.cpp.dotsT", "struct2.dots2.cpp.dotsT")
    enum_templates       = ("enum.dots.h.dotsT", "enum.dots.cpp.dotsT")

    # Default is C++ mapping
    type_mapping         = {
        "bool": "bool",
        "int8": "int8_t",
        "int16": "int16_t",
        "int32": "int32_t",
        "int64": "int64_t",
        "uint8": "uint8_t",
        "uint16": "uint16_t",
        "uint32": "uint32_t",
        "uint64": "uint64_t",
        "float32": "float",
        "float64": "double",
        "float128": "long double",
        "duration": "Duration",
        "timepoint": "TimePoint",
        "steady_timepoint": "SteadyTimePoint",
        "string": "std::string",
        "dots::property_set": "dots::property_set"
    }

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

    def generateEnum(self, enum, s):
        fs = enum
        fs["imports"] = s["imports"]
        fs["includes"] = []

        outputNames = self.outputNames(enum["name"], self.enum_templates)

        if self.list_generated:
            self.printOutputNames(outputNames)
            return
        
        if self.verbose:
            eprint("  Enum %s" % enum["name"])
        
        for key in outputNames:
            on = outputNames[key]
            
            fileName = on
            if self.verbose:
                eprint("    gen " + fileName)
            jinja = DdlTemplate(self.templatePath,  self.outputPath + "/" + fileName)
            jinja.render(key, fs)
    
    def generateStruct(self, struct, s):
        fs = struct
        fs["includes"] = []
        
        structTypes = []
        for attr in struct["attributes"]:
            if attr["vector"]:
                structTypes.append(attr["vector_type"])
            else:
                structTypes.append(attr["type"])
        needToImport = set(s["imports"]) & set(structTypes)
        fs["imports"] = list(needToImport)

        outputNames = self.outputNames(struct["name"], self.struct_templates)
        
        if self.list_generated:
            self.printOutputNames(outputNames)
            return
    
        if self.verbose:
            eprint("  Struct %s" % struct["name"])
        
        for key in outputNames:
            on = outputNames[key]
            
            fileName = on
            if self.verbose:
                eprint("    gen " + fileName)
            jinja = DdlTemplate(self.templatePath,  self.outputPath + "/" + fileName)
            jinja.render(key, fs)


    def processFile(self, fileName):
        if self.verbose:
            eprint("Process file " + fileName)
        fd = open(fileName, "r")

        outputPath = self.outputPath

        bn = os.path.basename(fileName)

        gen = DdlParser()
        s = gen.parse(fd.read())

        for enum in s["enums"]:
            self.generateEnum(enum, s)

        for struct in s["structs"]:
            self.generateStruct(struct, s)

    
if __name__ == "__main__":
    usage = "usage: %prog [options] dots-files"
    parser = OptionParser(usage=usage)
    parser.add_option("-C", "--config", dest="configFile")
    parser.add_option("-T", "--templatePath", dest="templatePath",
                    help="path to directory with template-files")
    parser.add_option("-o", "--outputPath", dest="outputPath", default=".",
                    help="path of output files")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="verbose output")
    parser.add_option("-M", "--list-generated", dest="list_generated", action="store_true", default=False, help="list generated output files")

    (options, args) = parser.parse_args()

    dcg = DotsCodeGenerator()
    if os.environ.has_key("DOTS_TEMPLATE_PATH"):
        dcg.templatePath = os.environ["DOTS_TEMPLATE_PATH"]
    if os.environ.has_key("DCG_CONFIG_FILE"):
        dcg.configFile = os.environ["DCG_CONFIG_FILE"]
    if options.templatePath is not None:
        dcg.templatePath = options.templatePath
    if options.list_generated:
        dcg.list_generated = options.list_generated
    if options.verbose:
        dcg.verbose = True
    dcg.outputPath = options.outputPath

    if dcg.verbose:
        eprint("Templatepath: '%s'" % options.templatePath)
        eprint("Output generated:", options.list_generated)

    for file in args:
        dcg.processFile(file)

