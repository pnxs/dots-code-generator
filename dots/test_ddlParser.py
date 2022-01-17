from unittest import TestCase
from dots.parser import DdlParser


class TestDdlParser(TestCase):
    def test_parse(self):
        test_data1 = """
        //a file comment
        import SharedMemStatus
        import SharedMemObjectReference

        struct SharedMemObject 
        {
            // Describes an instance of a shared memory object
            1: [key] string node;
            2: [key] string id;
            3: uint32 size;
            4: SharedMemStatus status;
            5: SharedMemObjectReference replicationSrc; // reference to origin, only set when object was replicated
            6: bool partialReplication; 
        }

        """

        parser = DdlParser()

        s = parser.parse(test_data1)

        self.assertEqual(s["imports"], ['SharedMemStatus', 'SharedMemObjectReference'])
        self.assertEqual(len(s["enums"]), 0)
        self.assertEqual(len(s["structs"]), 1)

        struct = s["structs"][0]

        attrs = struct["attributes"]

        self.assertEqual(struct["name"], "SharedMemObject")
        self.assertEqual(len(attrs), 6)

        self.assertEqual(attrs[0]["type"], "string")
        self.assertEqual(attrs[0]["tag"], 1)
        self.assertEqual(attrs[0]["options"], {'key': True})
        self.assertEqual(attrs[0]["cxx_type"], "string")
        self.assertEqual(attrs[0]["Name"], "Node")
        self.assertEqual(attrs[0]["name"], "node")
        self.assertEqual(attrs[0]["vector"], False)
        self.assertEqual(attrs[0]["key"], True)

        self.assertEqual(attrs[1]["type"], "string")
        self.assertEqual(attrs[1]["tag"], 2)
        self.assertEqual(attrs[1]["options"], {'key': True})
        self.assertEqual(attrs[1]["cxx_type"], "string")
        self.assertEqual(attrs[1]["Name"], "Id")
        self.assertEqual(attrs[1]["name"], "id")
        self.assertEqual(attrs[1]["vector"], False)
        self.assertEqual(attrs[1]["key"], True)

        self.assertEqual(attrs[2]["type"], "uint32")
        self.assertEqual(attrs[2]["tag"], 3)
        self.assertTrue("options" not in attrs[2])
        self.assertEqual(attrs[2]["cxx_type"], "uint32")
        self.assertEqual(attrs[2]["Name"], "Size")
        self.assertEqual(attrs[2]["name"], "size")
        self.assertEqual(attrs[2]["vector"], False)
        self.assertEqual(attrs[2]["key"], False)
