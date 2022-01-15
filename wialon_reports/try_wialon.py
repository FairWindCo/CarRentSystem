# Initialize Wialon instance
from wialon.sdk import WialonSdk, WialonError, SdkException

import environ

root = environ.Path(__file__)
env = environ.Env()
environ.Env.read_env()  # reading .env file

if __name__ == '__main__':
    token = env.str('WIALON_KEY')

    sdk = WialonSdk(
        is_development=True,
        scheme='https',
        host='local.overseer.ua',
        port=0,
        session_id='',
        extra_params={}
    )

    try:
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
