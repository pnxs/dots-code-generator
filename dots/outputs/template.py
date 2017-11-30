
from dots.outputs.output import Output
from dots.model import StructDescriptorData, EnumDescriptorData
from dots import DdlTemplate
import sys
import filecmp
import os

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

class Template(Output):
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

    def __init__(self, types, target_path):
        Output.__init__(self)
        self.types = types
        self.target_path = target_path
        self.verbose = True

        self.outputPath = self.target_path

    def list_generated_files(self):
        files = []
        for t in self.types:
            descriptor = self.types[t]
            target_file_name = self.getTargetFilename(descriptor)
            files.append(target_file_name + ".h")
            files.append(target_file_name + ".cpp")

        return files

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

    def loadConfig(self, configFile):
        if self.verbose:
            eprint("Load config from file %s" % configFile)
        config = __import__(configFile)

        if config:
            self.struct_templates = config.struct_templates
            self.enum_templates = config.enum_templates
            self.type_mapping = config.type_mapping
            self.vector_format = config.vector_format

    def printOutputNames(self, outputNames):
        for key in outputNames:
            on = outputNames[key]
            print(on)

    def generate(self):
        for t in self.types:
            descriptor = self.types[t]

            if isinstance(descriptor, StructDescriptorData):
                self.generateStruct(descriptor)
            elif isinstance(descriptor, EnumDescriptorData):
                pass
                #self.generateEnum(descriptor)
            else:
                raise Exception("unkown type of descriptor: " + descriptor.__class__)

    def generateFile(self, fileName, key, fs):
        absFileName = self.outputPath + "/" + fileName
        absTempFileName = absFileName + ".tmp"

        if self.verbose:
            eprint("    gen " + fileName)
        jinja = DdlTemplate(self.templatePath, absTempFileName)
        jinja.render(key, fs)

        # Check if tempFileName is different to fileName, only overwrite if different
        if not self.isFileEqual(absTempFileName, absFileName):
            os.rename(absTempFileName, absFileName)
        else:
            os.remove(absTempFileName)

    def generateEnum(self, descriptor):

        fs = {}
        #fs["imports"] = s["imports"]
        fs["includes"] = []
        fs["defines"] = self.defines

        outputNames = self.outputNames(fs["name"], self.enum_templates)

        if self.list_generated:
            self.printOutputNames(outputNames)
            return

        if self.verbose:
            eprint("  Enum %s" % fs["name"])

        for key in outputNames:
            self.generateFile(outputNames[key], key, fs)

    def descriptorToMap(self, descriptor):
        fs = {}
        fs["options"] = {
            "cached": descriptor.flags.cached,
            "cleanup": descriptor.flags.cleanup,
            "internal": descriptor.flags.internal,
            "local": descriptor.flags.local,
            "persistent": descriptor.flags.persistent,
            "substructOnly": descriptor.flags.substructOnly
        }

        fs["keys"] = []
        fs["attributes"] = []
        fs["keyAttributes"] = []

        for property in descriptor.properties:
            cxx_type = property.type
            if property.type in self.type_mapping:
                cxx_type = self.type_mapping[property.type]

            isVector = property.type.startswith("vector<")

            attr = {
                "type": property.type,
                "multiline_comment": "",
                "tag": property.tag,
                "name": property.name,
                "options": {},
                "Name": property.name[0].upper() + property.name[1:],
                "key": property.isKey,
                "vector": isVector,
                "cxx_type": cxx_type
            }

            if property.comment:
                attr["comment"] = property.comment


            if attr["key"]:
                fs["keys"].append(attr["name"])
                fs["keyAttributes"].append(attr)

            fs["attributes"].append(attr)

        fs["name"] = descriptor.name
        fs["structComment"] = descriptor.documentation.comment


        return fs

    def generateStruct(self, descriptor):
        fs = self.descriptorToMap(descriptor)
        fs["includes"] = []
        fs["defines"] = self.defines
        fs["imports"] = []

        print("Fs: ", fs)

        self.processOptions(fs["options"])

        print("generate struct", descriptor.name)

        # Build list of self defined struct types
        structTypes = []
        for attr in fs["attributes"]:
            t = None
            if attr["vector"]:
                t = attr["vector_type"]
            else:
                t = attr["type"]

            if t not in self.type_mapping:
                structTypes.append(t)

        # Filter any imports, that are not needed by this struct
        needToImport = set(fs["imports"]) & set(structTypes)
        # Add missing imports for struct
        needToImport = needToImport | set(structTypes)
        fs["imports"] = list(needToImport)

        outputNames = self.outputNames(fs["name"], self.struct_templates)

        print("Outputnames:", outputNames)

        if self.list_generated:
            self.printOutputNames(outputNames)
            return

        if self.verbose:
            eprint("  Struct %s" % fs["name"])

        for key in outputNames:
            self.generateFile(outputNames[key], key, fs)

    def getTargetFilename(self, descriptor):
        return self.target_path + "/" + descriptor.name + ".dots"

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