# Initialize Wialon instance
from wialon_reports.sdk import WialonSdk, SdkException, WialonError

sdk = WialonSdk(
    is_development=True,
    scheme='https',
    host='local.overseer.ua',
    port=0,
    session_id='',
    extra_params={}
)

try:
    token = 'db69899bb2d08b9d3804ffd183ff20ac1164DB3636204B7114E158B9152BB1A9E4B414A1'
    # If you haven't a token, you should use our token generator
    # https://goldenmcorp.com/resources/token-generator
    response = sdk.login(token)
    print(response)

    parameters = {
        'spec': {
            'itemsType': str,
            'propName': str,
            'propValueMask': str,
            'sortType': str,
            'propType': str,
            'or_logic': bool
        },
        'force': int,
        'flags': int,
        'from': int,
        'to': int
    }

    units = sdk.core_search_items(parameters)
    print(units)

    sdk.logout()
except SdkException as e:
    print(f'Sdk related error: {e}')
except WialonError as e:
    print(f'Wialon related error: {e}')
except Exception as e:
    print(f'Python error: {e}')
