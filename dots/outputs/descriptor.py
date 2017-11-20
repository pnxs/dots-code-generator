
import dots
from dots.model import StructDescriptorData, EnumDescriptorData, DotsHeader
import cbor
from dots.outputs.output import Output
import logging


class Descripor(Output):
    def __init__(self, types, target_path):
        Output.__init__(self)
        self.types = types
        self.target_path = target_path

    def list_generated_files(self):
        files = []
        for t in self.types:
            descriptor = self.types[t]
            files.append(self.getTargetFilename(descriptor))

        return files

    def generate(self):
        for t in self.types:
            dots_type = self.types[t]
            self.store_descriptor(dots_type)

    def getTargetFilename(self, descriptor):
        return self.target_path + "/" + descriptor.name + ".doi"

     def store_descriptor(self, descriptor):
        dh = DotsHeader()

        file_name = self.getTargetFilename(descriptor)

        if isinstance(descriptor, StructDescriptorData):
            dh.typeName = "StructDescriptorData"
        elif isinstance(descriptor, EnumDescriptorData):
            dh.typeName = "EnumDescriptorData"
        else:
            raise Exception("unkown type of descriptor: " + descriptor.__class__)

        logging.info("store descriptor '%s' into %s" % (descriptor.name, file_name))

        bin_dh = cbor.dumps(dots.serialize_object(dh))

        output_file = open(file_name, "wb")

        bin_payload = cbor.dumps(dots.serialize_object(descriptor))

        output_file.write(bin_dh)
        output_file.write(bin_payload)

        output_file.close()
