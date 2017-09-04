from unittest import TestCase
from dcg import DotsCodeGenerator

class TestDotsCodeGenerator(TestCase):
    def test_isFileEqual(self):
        dcg = DotsCodeGenerator()
        dcg.verbose = True
        self.assertTrue(dcg.isFileEqual("./tests/cmp_test_1", "./tests/cmp_test_equal_to_1"))
        self.assertFalse(dcg.isFileEqual("./tests/cmp_test_1", "./tests/cmp_test_2"))
