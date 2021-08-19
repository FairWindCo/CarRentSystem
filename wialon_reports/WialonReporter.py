import datetime

from wialon import Wialon, WialonError, flags


class WialonReporter:
    def __init__(self, api, server='local.overseer.ua') -> None:
        super().__init__()
        try:
            self.wialon_api = Wialon(host=server)

            self.account = self.wialon_api.token_login(
                token=api)
            print(self.account)
            self.wialon_api.sid = self.account['eid']
            self.wialon_api.avl_evts()

        except WialonError as e:
            self.wialon_api = None
            self.last_error = e

    def get_reports_list(self):
        if not self.wialon_api:
            return []
        spec = {
            'itemsType': 'avl_resource',
            'propName': '',
            'propValueMask': '',
            'sortType': '',
            'or_logic': False
        }
        interval = {"from": 0, "to": 0}
        items = []
        try:
            units = self.wialon_api.core_search_items(spec=spec, force=1, flags=8193, **interval)
            if 'items' in units:
                items = [(item['id'], [(rep['id'], rep['n']) for id, rep in item['rep'].items()]) for item in
                         units['items']]
        except WialonError as e:
            self.last_error = e
        return items

    def get_monitoring_objects(self):
        if not self.wialon_api:
            return []
        spec = {
            'itemsType': 'avl_unit',
            'propName': 'sys_name',
            'propValueMask': '*',
            'sortType': 'sys_name'
        }
        interval = {"from": 0, "to": 0}
        try:
            units = self.wialon_api.core_search_items(spec=spec, force=1, flags=flags.ITEM_DATAFLAG_BASE, **interval)
            if 'totalItemsCount' in units and units['totalItemsCount'] > 0:
                return [(obj['nm'], obj['id']) for obj in units['items']]
        except WialonError as e:
            self.last_error = e
        return []

    def get_monitoring_objects_position(self):
        if not self.wialon_api:
            return []
        spec = {
            'itemsType': 'avl_unit',
            'propName': 'sys_name',
            'propValueMask': '*',
            'sortType': 'sys_name'
        }
        interval = {"from": 0, "to": 0}
        try:
            units = self.wialon_api.core_search_items(spec=spec, force=1,
                                                      flags=flags.ITEM_RESOURCE_ACCEESSFLAG_VIEW_POI, **interval)
            if 'items' in units:
                return [convert_position(item['pos']) for item in units['items']]
        except WialonError as e:
            self.last_error = e
        return []

    def get_objects_position(self, id):
        if not self.wialon_api:
            return None
        try:
            units = self.wialon_api.core_search_item(id=id, flags=flags.ITEM_RESOURCE_ACCEESSFLAG_VIEW_POI)
            if 'item' in units and 'pos' in units['item']:
                return convert_position(units['item']['pos'])
        except WialonError as e:
            self.last_error = e
        return None

    def get_report(self, resource_id: int, report_id: int, report_object: int, start_date: datetime,
                   end_date: datetime, table=None):
        if not self.wialon_api:
            return []
        try:
            units = self.wialon_api.report_cleanup_result()
            if units['error'] != 0:
                return []
            interval = {"from": int(start_date.timestamp()),
                        "to": int(end_date.timestamp()),
                        "flags": 0}
            report = self.wialon_api.report_exec_report(reportResourceId=resource_id, reportTemplateId=report_id,
                                                        reportObjectId=report_object,
                                                        reportObjectSecId=0, interval=interval)
            report_tables = report['reportResult']['tables']
            if table is None:
                return [(table,
                         self.wialon_api.report_get_result_rows(tableIndex=index, indexFrom=0, indexTo=table['rows']))
                        for index, table in enumerate(report_tables)]
            else:
                if table in [0, len(report_tables)]:
                    last_row = report_tables[table]['rows']
                    report_date = self.wialon_api.report_get_result_rows(tableIndex=table, indexFrom=0,
                                                                         indexTo=last_row)
                    return [(report_tables[table], report_date)]
        except WialonError as e:
            self.last_error = e
            return []

    def __del__(self):
        if self.wialon_api:
            try:
                self.wialon_api.core_logout()
            except WialonError as e:
                self.last_error = e


def convert_row(row):
    return {
        'num': row[0],
        'start_time': datetime.datetime.fromtimestamp(row[1]['v']),
        'start_position': (row[2]['y'], row[2]['x']),
        'end_time': datetime.datetime.fromtimestamp(row[3]['v']),
        'end_position': (row[4]['y'], row[4]['x']),
        'time': row[5],
        'total_time': row[6],
        'millage': row[7],
        'consumption_DUT': row[8],
        'consumption_calc': row[9],
        'avg_consumption_DUT': row[10],
        'avg_consumption_calc': row[11],
        'gasoline_before': row[12],
        'gasoline_after': row[13],
    }


def convert_position(position_struct):
    if position_struct:
        return {
            'time': datetime.datetime.fromtimestamp(position_struct['t']),
            'y': position_struct['y'],
            'x': position_struct['x'],
            'altitude': position_struct['z'],
            'speed': position_struct['s'],
            'course': position_struct['c'],
            'satellite': position_struct['sc'],
        }
    else:
        return None
