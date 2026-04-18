import unittest

from dots import DdlParser

class TestExtensions(unittest.TestCase):
    maxDiff = 4096

    def test_config_py(self):
        gen = DdlParser()
        s = gen.parse(testData1)
        self.assertEqual(resultData1, s)




if __name__ == '__main__':
    unittest.main()