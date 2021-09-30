import unittest

from request_processor.tests.test_prototypedescription import ExampleClass
from request_processor.value_utility import ValueAccessor


class AccessObjectTest(unittest.TestCase):

    def test_get_value(self):
        prototypes = ValueAccessor(['field_2'])
        obj = ExampleClass()
        self.assertEqual(prototypes.get_object_member(obj), [10, 20, 30])

    def test_set_value(self):
        prototypes = ValueAccessor(['field_2', '0'])
        obj = ExampleClass()
        self.assertEqual(prototypes.get_object_member(obj), 10)
        prototypes.modify_object_member(obj, 20)
        self.assertEqual(prototypes.get_object_member(obj), 20)
