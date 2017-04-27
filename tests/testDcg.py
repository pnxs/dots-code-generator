import unittest

from dots import DdlParser

testData1 = """
//a file comment
import SharedMemStatus
import SharedMemObjectReference

struct SharedMemObject 
{
    // Describes an instance of a shared memory object
    1: [key] string node;
    2: [key] string id;
    3: uint32_t size;
    4: SharedMemStatus status;
    5: SharedMemObjectReference replicationSrc; // reference to origin, only set when object was replicated
    6: bool partialReplication; 
}

"""

resultData1 = {'imports': ['SharedMemStatus', 'SharedMemObjectReference'], 'enums': [], 'structs': [
    {'name': 'SharedMemObject', 'keys': ['node', 'id'],
     'structComment': 'Describes an instance of a shared memory object', 'attributes': [
        {'cxx_type': 'string', 'name': 'node', 'tag': 1, 'vector': False, 'key': True, 'type': 'string',
         'options': {'key': True}, 'Name': 'Node'},
        {'cxx_type': 'string', 'name': 'id', 'tag': 2, 'vector': False, 'key': True, 'type': 'string',
         'options': {'key': True}, 'Name': 'Id'},
        {'key': False, 'name': 'size', 'tag': 3, 'vector': False, 'cxx_type': 'uint32_t', 'type': 'uint32_t',
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

#################################################################

testData2 = """
enum SpMsgType {
    1: regular = 0,
    2: join,
    3: leave,
    4: kill,
    5: groups,
    6: membership,
    7: transition // transition membership message
}
"""

resultData2 = {'enums': [{'items': [{'name': 'regular', 'tag': 1, 'value': 0},
                                    {'name': 'join', 'tag': 2, 'value': 1},
                                    {'name': 'leave', 'tag': 3, 'value': 2},
                                    {'name': 'kill', 'tag': 4, 'value': 3},
                                    {'name': 'groups', 'tag': 5, 'value': 4},
                                    {'name': 'membership', 'tag': 6, 'value': 5},
                                    {'comment': 'transition membership message',
                                     'name': 'transition',
                                     'tag': 7,
                                     'value': 6}],
                          'name': 'SpMsgType'}],
               'imports': [],
               'structs': []}


class TestDotsParser(unittest.TestCase):
    maxDiff = 4096

    def test_parsing1(self):
        gen = DdlParser()
        s = gen.parse(testData1)
        self.assertEqual(s, resultData1)

    def test_parsing2(self):
        gen = DdlParser()
        s = gen.parse(testData2)
        self.assertEqual(s, resultData2)
        

if __name__ == '__main__':
    unittest.main()
