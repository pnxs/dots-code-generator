import unittest

from lark import Lark
from dots import DotsTransformer
from dots.parser import type_mapping_1_1
import pprint

testData1 = """
//a file comment
import SharedMemStatus
import SharedMemObjectReference

/// Describes an instance of a shared memory object
struct SharedMemObject 
{
    1: [key] string node;
    2: [key] string id;
    3: uint32 size;
    4: SharedMemStatus status;
    5: SharedMemObjectReference replicationSrc; /// reference to origin, only set when object was replicated
    6: bool partialReplication; 
}

"""

resultData1 = {'imports': ['SharedMemStatus', 'SharedMemObjectReference'], 'enums': [], 'structs': [
    {'name': 'SharedMemObject', 'keys': ['node', 'id'],
     'structComment': ['Describes an instance of a shared memory object'], 'attributes': [
        {'cxx_type': 'string', 'name': 'node', 'tag': 1, 'vector': False, 'key': True, 'type': 'string',
         'options': {'key': True}, 'Name': 'Node'},
        {'cxx_type': 'string', 'name': 'id', 'tag': 2, 'vector': False, 'key': True, 'type': 'string',
         'options': {'key': True}, 'Name': 'Id'},
        {'key': False, 'name': 'size', 'tag': 3, 'vector': False, 'cxx_type': 'uint32', 'type': 'uint32',
         'Name': 'Size'}, {'key': False, 'name': 'status', 'tag': 4, 'vector': False, 'cxx_type': 'SharedMemStatus',
                           'type': 'SharedMemStatus', 'Name': 'Status'},
        {'comment': 'reference to origin, only set when object was replicated', 'cxx_type': 'SharedMemObjectReference',
         'name': 'replicationSrc', 'tag': 5, 'vector': False, 'key': False, 'type': 'SharedMemObjectReference',
         'Name': 'ReplicationSrc'},
        {'key': False, 'name': 'partialReplication', 'tag': 6, 'vector': False, 'cxx_type': 'bool', 'type': 'bool',
         'Name': 'PartialReplication'}], 'keyAttributes': [
        {'cxx_type': 'string', 'name': 'node', 'tag': 1, 'vector': False, 'key': True, 'type': 'string',
         'options': {'key': True}, 'Name': 'Node'},
        {'cxx_type': 'string', 'name': 'id', 'tag': 2, 'vector': False, 'key': True, 'type': 'string',
         'options': {'key': True}, 'Name': 'Id'}], 'options': {}}]}

testData2 = """
enum SpMsgType {
    1: regular = 0,
    2: join,
    3: leave,
    4: kill,
    5: groups,
    6: membership,
    7: transition /// transition membership message
}

"""

resultData2 = {
    'enums': [
    {
        'items': [
            {'name': 'regular', 'Name': 'Regular', 'tag': 1, 'value': 0},
            {'name': 'join', 'Name': 'Join', 'tag': 2, 'value': 1},
            {'name': 'leave', 'Name': 'Leave', 'tag': 3, 'value': 2},
            {'name': 'kill', 'Name': 'Kill', 'tag': 4, 'value': 3},
            {'name': 'groups', 'Name': 'Groups', 'tag': 5, 'value': 4},
            {'name': 'membership', 'Name': 'Membership', 'tag': 6, 'value': 5},
            {'comment': 'transition membership message', 'name': 'transition', 'Name': 'Transition', 'tag': 7, 'value': 6}
        ],
        'Name': 'SpMsgType',
        'name': 'SpMsgType'
    }],
    'imports': [],
    'structs': []
}

testData3 = """
import SharedMemStatus
import SharedMemObjectReference

struct SharedMemObject 
{
    1: [key] string node;
    2: [key] string id;
    3: vector<uint32> intVector;
    4: vector<SharedMemStatus> typeVector;
}

"""

resultData3 = {
    'imports': [
        'SharedMemStatus', 'SharedMemObjectReference'
    ],
    'enums': [],
    'structs': [
        {'name': 'SharedMemObject', 'keys': ['node', 'id'], 'attributes': [
            {'cxx_type': 'string', 'name': 'node', 'tag': 1, 'vector': False, 'key': True, 'type': 'string', 'options': {'key': True}, 'Name': 'Node'},
            {'cxx_type': 'string', 'name': 'id', 'tag': 2, 'vector': False, 'key': True, 'type': 'string', 'options': {'key': True}, 'Name': 'Id'},
            {'key': False, 'name': 'intVector', 'tag': 3, 'vector': True, 'vector_type': 'uint32', 'cxx_type': 'list', 'cxx_vector_type': 'uint32', 'type': 'vector<uint32>', 'Name': 'IntVector'},
            {'key': False, 'name': 'typeVector', 'tag': 4, 'vector': True, 'vector_type': 'SharedMemStatus', 'cxx_type': 'list', 'cxx_vector_type': 'SharedMemStatus', 'type': 'vector<SharedMemStatus>', 'Name': 'TypeVector'},
        ],
        'keyAttributes': [
            {'cxx_type': 'string', 'name': 'node', 'tag': 1, 'vector': False, 'key': True, 'type': 'string', 'options': {'key': True}, 'Name': 'Node'},
            {'cxx_type': 'string', 'name': 'id', 'tag': 2, 'vector': False, 'key': True, 'type': 'string', 'options': {'key': True}, 'Name': 'Id'}
        ],
        'options': {}
        }
    ]
}

pp = pprint.PrettyPrinter(indent=4)

class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.ddlconfig = {
            "vector_format": "list",
            "type_mapping": type_mapping_1_1
        }
        with open("../dots.lark") as f:
            self.parser = parser = Lark(f, start='start', parser="lalr", maybe_placeholders=True)

    def test_parse1(self):
        tree = self.parser.parse(testData1)
        tree = DotsTransformer(self.ddlconfig).transform(tree)
        pp.pprint(tree)
        self.assertEqual(resultData1, tree)

    def test_parse2(self):
        tree = self.parser.parse(testData2)
        tree = DotsTransformer(self.ddlconfig).transform(tree)
        pp.pprint(tree)
        self.assertEqual(resultData2, tree)

    def test_parse3(self):
        tree = self.parser.parse(testData3)
        tree = DotsTransformer(self.ddlconfig).transform(tree)
        pp.pprint(tree)
        self.assertEqual(resultData3, tree)


if __name__ == '__main__':
    unittest.main()
