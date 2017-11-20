#!/usr/bin/env python

"""
Dots Code Generator
"""

from __future__ import print_function
from optparse import OptionParser
from dots import DdlParser, DdlTemplate
import os

import sys
import filecmp
import functools
import itertools
import operator

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

class DotsCodeGenerator:


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

    def isExisting(self, fileName):
        try:
            ret = os.stat(fileName)
            return True
        except:
            return False

    def isFileEqual(self, left, right):
        try:
            if not self.isExisting(left):
                return False
            if not self.isExisting(right):
                return False
            ret = filecmp.cmp(left, right, shallow=False)
            #eprint("Check ", left, right, ret)
            return ret
        except Exception as e:
            eprint("Exception:", e)
            return False



    
if __name__ == "__main__":
    usage = "usage: %prog [options] dots-files"
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
    if os.environ.has_key("DOTS_TEMPLATE_PATH"):
        dcg.templatePath = os.environ["DOTS_TEMPLATE_PATH"]
    if os.environ.has_key("DCG_CONFIG_FILE"):
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
    
        
