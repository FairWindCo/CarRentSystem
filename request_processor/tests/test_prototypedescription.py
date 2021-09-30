import datetime
import unittest

from request_processor.value_utility import PrototypedValueAccessor


class ExampleClass:
    field_1 = 10
    field_2 = [10, 20, 30]
    field_3 = {'test1': 10, 'test_2': 20}
    field_4 = '10/05/2021 13:16:04'
    field_5 = 12.2
    field_6 = {'test6': {'test1.1': 661.1, 'test_2.1': 20}, 'test7': [10, 20, 30]}
    field_7 = datetime.datetime.now()
    field_8 = '12.2'
    field_9 = '33'


class PrototypeDescriptionTest(unittest.TestCase):

    def test_convert_from_string(self):
        prototype = PrototypedValueAccessor.parse_one('test')

        self.assertEqual(prototype.field_name, 'test')
        self.assertEqual(prototype.result_field_name, 'test')

    def test_convert_from_complex_string(self):
        prototype = PrototypedValueAccessor.parse_one('field_name::default_value::method::result_field')

        self.assertEqual(prototype.field_name, 'field_name')
        self.assertEqual(prototype.result_field_name, 'result_field')
        self.assertEqual(prototype.convertor, 'method')
        self.assertEqual(prototype.default_value, 'default_value')

    def test_convert_from_array(self):
        prototype = PrototypedValueAccessor.parse_one(['field_name', 'default_value', 'method', 'result_field'])

        self.assertEqual(prototype.field_name, 'field_name')
        self.assertEqual(prototype.result_field_name, 'result_field')
        self.assertEqual(prototype.convertor, 'method')
        self.assertEqual(prototype.default_value, 'default_value')

    def test_convert_from_dict(self):
        prototype = PrototypedValueAccessor.parse_one({
            'field_name': 'field_name',
            'convertor': 'method',
            'default_value': 'default_value',
            'result_field_name': 'result_field'})

        self.assertEqual(prototype.field_name, 'field_name')
        self.assertEqual(prototype.result_field_name, 'result_field')
        self.assertEqual(prototype.convertor, 'method')
        self.assertEqual(prototype.default_value, 'default_value')

    def test_convert_from_array_with_not_string(self):
        prototype = PrototypedValueAccessor.parse_one(['field_name', 5, 'method', 'result_field'])

        self.assertEqual(prototype.field_name, 'field_name')
        self.assertEqual(prototype.result_field_name, 'result_field')
        self.assertEqual(prototype.convertor, 'method')
        self.assertEqual(prototype.default_value, 5)

    def test_convert_from_dict_with_not_string(self):
        prototype = PrototypedValueAccessor.parse_one({
            'field_name': 'field_name',
            'convertor': 'method',
            'default_value': 5.5,
            'result_field_name': 'result_field'})

        self.assertEqual(prototype.field_name, 'field_name')
        self.assertEqual(prototype.result_field_name, 'result_field')
        self.assertEqual(prototype.convertor, 'method')
        self.assertEqual(prototype.default_value, 5.5)

    def test_convert_from_string_complex(self):
        prototypes = PrototypedValueAccessor.from_description('test1, test2 , test 3')

        self.assertEqual(prototypes[0].field_name, 'test1')
        self.assertEqual(prototypes[0].result_field_name, 'test1')

        self.assertEqual(prototypes[1].field_name, 'test2')
        self.assertEqual(prototypes[1].result_field_name, 'test2')

        self.assertEqual(prototypes[2].field_name, 'test 3')
        self.assertEqual(prototypes[2].result_field_name, 'test 3')

    def test_convert_from_string_complex2(self):
        prototypes = PrototypedValueAccessor.from_description('testf::default_value1::method1::result_field1, '
                                                           'test2 , test 3::default_value3::method3::result_field3')

        self.assertEqual(prototypes[0].field_name, 'testf')
        self.assertEqual(prototypes[0].result_field_name, 'result_field1')
        self.assertEqual(prototypes[0].convertor, 'method1')
        self.assertEqual(prototypes[0].default_value, 'default_value1')

        self.assertEqual(prototypes[1].field_name, 'test2')
        self.assertEqual(prototypes[1].result_field_name, 'test2')

        self.assertEqual(prototypes[2].field_name, 'test 3')
        self.assertEqual(prototypes[2].result_field_name, 'result_field3')
        self.assertEqual(prototypes[2].convertor, 'method3')
        self.assertEqual(prototypes[2].default_value, 'default_value3')

    def test_field_path(self):
        prototypes = PrototypedValueAccessor('field1__field2__field3')
        self.assertEqual(prototypes.field_path, ['field1', 'field2', 'field3'])

    def test_field_path_suffix(self):
        prototypes = PrototypedValueAccessor('field5__field6__field7__lt')
        self.assertEqual(prototypes.field_path, ['field5', 'field6', 'field7'])
        self.assertEqual(prototypes.field_suffix, '__lt')

    def test_convert_from_complex_dict(self):
        prototypes = PrototypedValueAccessor.from_description({
            'test1': 'default_value1:: method1::result_field1',
            'test2': None,
            'test 3': 'default_value3::method3::result_field3'})

        self.assertEqual(prototypes[0].field_name, 'test1')
        self.assertEqual(prototypes[0].result_field_name, 'result_field1')
        self.assertEqual(prototypes[0].convertor, 'method1')
        self.assertEqual(prototypes[0].default_value, 'default_value1')

        self.assertEqual(prototypes[1].field_name, 'test2')
        self.assertEqual(prototypes[1].result_field_name, 'test2')

        self.assertEqual(prototypes[2].field_name, 'test 3')
        self.assertEqual(prototypes[2].result_field_name, 'result_field3')
        self.assertEqual(prototypes[2].convertor, 'method3')
        self.assertEqual(prototypes[2].default_value, 'default_value3')

    def test_get_value_1(self):
        prototypes = PrototypedValueAccessor('field_1')
        obj = ExampleClass()
        self.assertEqual(prototypes.field_path, ['field_1'])
        self.assertEqual(prototypes.get_object_member(obj), 10)

    def test_get_value_2(self):
        prototypes = PrototypedValueAccessor('field_2__1')
        obj = ExampleClass()
        self.assertEqual(prototypes.field_path, ['field_2', '1'])
        self.assertEqual(prototypes.get_object_member(obj), 20)

    def test_get_value_3(self):
        prototypes = PrototypedValueAccessor('field_2__0')
        obj = ExampleClass()
        self.assertEqual(prototypes.field_path, ['field_2', '0'])
        self.assertEqual(prototypes.get_object_member(obj), 10)

    def test_get_value_4(self):
        prototypes = PrototypedValueAccessor('field_6__test6__test1.1')
        obj = ExampleClass()
        self.assertEqual(prototypes.field_path, ['field_6', 'test6', 'test1.1'])
        self.assertEqual(prototypes.get_object_member(obj), 661.1)

    def test_get_value_default_1(self):
        prototypes = PrototypedValueAccessor('field_55__test6__test1.1', 35)
        obj = ExampleClass()
        self.assertEqual(prototypes.field_path, ['field_55', 'test6', 'test1.1'])
        self.assertEqual(prototypes.get_object_member(obj), 35)

    def test_get_value_default_2(self):
        prototypes = PrototypedValueAccessor('field_66__test66__test1.1', 35)
        obj = ExampleClass()
        self.assertEqual(prototypes.field_path, ['field_66', 'test66', 'test1.1'])
        self.assertEqual(prototypes.get_object_member(obj), 35)

    def test_get_value_default_3(self):
        prototypes = PrototypedValueAccessor('field_55__test6__test1.1', None)
        obj = ExampleClass()
        self.assertEqual(prototypes.field_path, ['field_55', 'test6', 'test1.1'])
        self.assertIsNone(prototypes.get_object_member(obj))

    def test_get_converted_value_str_to_date(self):
        format = '%d/%m/%Y %H:%M:%S'
        prototypes = PrototypedValueAccessor('field_4', None, 'datetime_%d/%m/%Y %H:%M:%S', 'result')
        obj = ExampleClass()
        self.assertEqual(prototypes.get_result_value(obj), ('result', datetime.datetime.strptime(obj.field_4, format)))

    def test_get_converted_value_date_to_str(self):
        format = '%d/%m/%Y %H:%M:%S'
        prototypes = PrototypedValueAccessor('field_7', None, 'datetime_%d/%m/%Y %H:%M:%S', 'result')
        obj = ExampleClass()
        self.assertEqual(prototypes.get_result_value(obj), ('result', obj.field_7.strftime(format)))

    def test_get_converted_value_str_to_float(self):
        prototypes = PrototypedValueAccessor('field_8', None, 'float', 'result')
        obj = ExampleClass()
        self.assertEqual(prototypes.get_result_value(obj), ('result', obj.field_5))

    def test_get_converted_value_float_to_str(self):
        prototypes = PrototypedValueAccessor('field_5', None, 'format_{:.2f}', 'result')
        obj = ExampleClass()
        self.assertEqual(prototypes.get_result_value(obj), ('result', '12.20'))
