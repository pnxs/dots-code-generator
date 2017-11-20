
from dots.outputs.output import Output

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
        if dcg.verbose:
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
            dots_type = self.types[t]
            for enum in s["enums"]:
                self.check_consistency_enum(enum)
                self.generateEnum(enum, s)

            for struct in s["structs"]:
                self.check_consistency_struct(struct)
                self.generateStruct(struct, s)

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
        fs["imports"] = list(needToImport)

        outputNames = self.outputNames(struct["name"], self.struct_templates)

        if self.list_generated:
            self.printOutputNames(outputNames)
            return

        if self.verbose:
            eprint("  Struct %s" % struct["name"])

        for key in outputNames:
            self.generateFile(outputNames[key], key, fs)

    def getTargetFilename(self, descriptor):
        return self.target_path + "/" + descriptor.name + ".dots"