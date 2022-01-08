import unittest

from django_helpers.request_processor.filtering import FilterProcessor

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
]


class PrototypeDescriptionTest(unittest.TestCase):

    # value_name: Union[str, int], default_value: Any = None,
    #                 value_convertor: Union[str, Callable] = 'any', form_field_name: str = None,
    #                 form_convertor: Union[str, Callable]
    #

    def test_filter(self):
        processor = FilterProcessor([{
            'field_name': 'value',
            'form_field_name': 'filter',
            'form_convertor': 'int'

        }
        ])

        processor.read_filters_from_request({
            'GET': {
                'filter': '10',
            },
        })

        result = processor.process_filtering(TEST_ARRAY_DATA)
        self.assertEqual(list(result), RESULT_ARRAY_DATA)

