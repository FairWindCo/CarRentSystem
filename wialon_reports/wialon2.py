import datetime

from wialon import Wialon, flags, WialonError

import environ

root = environ.Path(__file__)
env = environ.Env()
environ.Env.read_env()  # reading .env file

if __name__ == '__main__':
    api_key = env.str('WIALON_KEY')

    try:
        wialon_api = Wialon(host='local.overseer.ua')
        # old username and password login is deprecated, use token login
        #result = wialon_api.token_login(token='db69899bb2d08b9d3804ffd183ff20ac1164DB3636204B7114E158B9152BB1A9E4B414A1')
        result = wialon_api.token_login(
            token=api_key)
        print('LOGIN:', result)
        print('reportResourceId=', result['user']['bact'])
        wialon_api.sid = result['eid']
        result = wialon_api.avl_evts()
        print('EVENTS: ', result)

        spec = {
            'itemsType': 'avl_unit',
            'propName': 'sys_name',
            'propValueMask': '*',
            'sortType': 'sys_name'
        }
        interval = {"from": 0, "to": 0}
        units = wialon_api.core_search_items(spec=spec, force=1, flags=flags.ITEM_DATAFLAG_BASE, **interval)
        print('reportObjectId is:')
        if 'totalItemsCount' in units and units['totalItemsCount'] > 0:
            for item in units['items']:
                print(item)

        spec = {
            'itemsType': 'avl_resource',
            'propName': '',
            'propValueMask': '',
            'sortType': '',
            'or_logic': False
        }
        interval = {"from": 0, "to": 0}
        units = wialon_api.core_search_items(spec=spec, force=1, flags=8193, **interval)
        print(units)
        units = wialon_api.core_search_items(spec=spec, force=1, flags=8192, **interval)
        print('REPORT INFO', units)

        print('TRY CLEAN REPORT')
        units = wialon_api.report_cleanup_result()
        print(units)
        print('TRY REPORT')
        interval = {"from": int(datetime.datetime(year=2021, month=8, day=10).timestamp()),
                    "to": int(datetime.datetime(year=2021, month=8, day=11).timestamp()),
                    "flags": 0}
        print(interval)
        result = wialon_api.report_exec_report(reportResourceId=112198,
                                               reportTemplateId=1,
                                               reportObjectId=112171,
                                               reportObjectSecId=0, interval=interval)
        print(result)

        result = wialon_api.report_get_result_rows(tableIndex=0,indexFrom=0,indexTo=5)
        print(result)

        wialon_api.core_logout()
    except WialonError as e:
        print(e)
