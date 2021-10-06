import unittest

from request_processor.sorting import SortProcessor

TEST_ARRAY_DATA = [
    {
        'name': 'First Name',
        'value': 10
    },
    {
        'name': 'Second Name',
        'value': 30
    },
    {
        'name': 'Third Name',
        'value': 20
    }
]

RESULT_ARRAY_DATA = [
    {
        'name': 'First Name',
        'value': 10
    },
    {
        'name': 'Third Name',
        'value': 20
    },
    {
        'name': 'Second Name',
        'value': 30
    },
]


class PrototypeDescriptionTest(unittest.TestCase):

    def test_sort(self):
        processor = SortProcessor()

        processor.read_sorting_parameters_from_request({
            'GET': {
                'sort_by': 'name',
            },
        })

        result = processor.process_sorting(TEST_ARRAY_DATA)
        self.assertEqual(result, TEST_ARRAY_DATA)

    def test_sort_2(self):
        processor = SortProcessor()

        processor.read_sorting_parameters_from_request({
            'GET': {
                'sort_by': 'value',
            },
        })

        result = processor.process_sorting(TEST_ARRAY_DATA)
        self.assertEqual(result, RESULT_ARRAY_DATA)
