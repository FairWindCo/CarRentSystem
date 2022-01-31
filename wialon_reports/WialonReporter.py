import datetime
import os
import pickle
from typing import Iterable

from wialon import Wialon, WialonError, flags

LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
UTC_TIMEZONE = datetime.timezone.utc


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
            if not report_tables:
                return [{'label': [], 'header': []}, []]
            if table is None:
                return [(table,
                         self.wialon_api.report_get_result_rows(tableIndex=index, indexFrom=0, indexTo=table['rows']))
                        for index, table in enumerate(report_tables)]
            else:
                if table in range(len(report_tables)):
                    last_row = report_tables[table]['rows']
                    report_date = self.wialon_api.report_get_result_rows(tableIndex=table, indexFrom=0,
                                                                         indexTo=last_row)
                    return [(report_tables[table], report_date)]
        except WialonError as e:
            self.last_error = e
            return []

    def _get_report_table(self, report_tables, index):
        if isinstance(index, str):
            for i, table in enumerate(report_tables):
                if index == table['name']:
                    return self._get_report_table_by_index(report_tables, i)
        elif isinstance(index, int):
            return self._get_report_table_by_index(report_tables, index)
        else:
            return None

    def _get_report_table_by_index(self, report_tables, index):
        if index in range(len(report_tables)):
            last_row = report_tables[index]['rows']
            report_date = self.wialon_api.report_get_result_rows(tableIndex=index, indexFrom=0,
                                                                 indexTo=last_row)
            return {
                'header': report_tables[index],
                'rows': report_date
            }
        return None

    def get_report_sub_lists_cached(self, resource_id: int, report_id: int, report_object: int, start_date: datetime,
                                    end_date: datetime, table, convertors=None, tzinfo=LOCAL_TIMEZONE, cache_path=None):
        file_path = None
        if cache_path is not None:
            file_path = os.path.join(cache_path,
                                     f"wialon_{resource_id}{report_id}{report_object}_\
{start_date.strftime('%d-%m-%y')}-{end_date.strftime('%d-%m-%y')}.dat")
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, "rb") as file:
                    return pickle.load(file)
        result = self.get_report_sub_lists(resource_id, report_id, report_object, start_date,
                                           end_date, table, convertors=convertors, tzinfo=tzinfo)
        if result and cache_path is not None and file_path:
            if not os.path.exists(f'{cache_path}'):
                os.mkdir(f'{cache_path}')
            with open(file_path, "wb") as file:
                pickle.dump(result, file)
        return result

    def get_report_sub_lists(self, resource_id: int, report_id: int, report_object: int, start_date: datetime,
                             end_date: datetime, table, convertors=None, tzinfo=LOCAL_TIMEZONE):

        empty = {
            'summary': {},
            'tables': []
        }
        if not self.wialon_api or table is None:
            return empty
        try:
            units = self.wialon_api.report_cleanup_result()
            if units['error'] != 0:
                return empty
            interval = {"from": date_to_int_timestamp(start_date, tzinfo),
                        "to": date_to_int_timestamp(end_date, tzinfo),
                        "flags": 0}

            report = self.wialon_api.report_exec_report(reportResourceId=resource_id, reportTemplateId=report_id,
                                                        reportObjectId=report_object,
                                                        reportObjectSecId=0, interval=interval)
            if 'reportResult' not in report:
                print('EMPTY REPORT ERROR')
                return empty
            report = report['reportResult']
            if 'stats' in report and report['stats']:
                empty['summary'] = convert_stats(report['stats'])
            if 'tables' in report and report['tables']:
                report_tables = report['tables']
                if not report_tables:
                    return empty
                if isinstance(table, int):
                    result = self._get_report_table(report_tables, table)
                    if result:
                        empty['tables'] = [convert_table_rows(result, convertors)]
                    return empty
                elif isinstance(table, Iterable):
                    empty['tables'] = list(
                        map(lambda e: convert_table_rows(e, convertors), filter(lambda m: bool(m), [
                            self._get_report_table(report_tables, index) for index in table])))
                    return empty
                else:
                    return empty
            else:
                print('WIALON NO TABLE')
                return empty
        except WialonError as e:
            self.last_error = e
            print('WIALON ERROR')
            return empty

    def __del__(self):
        if self.wialon_api:
            try:
                self.wialon_api.core_logout()
            except WialonError as e:
                self.last_error = e


def convert_stats(data):
    return {
        'report_name': data[0][1],
        'object_name': data[1][1],
        'start_interval': datetime.datetime.strptime(data[2][1], "%Y-%m-%d %H:%M:%S").astimezone(LOCAL_TIMEZONE),
        'end_interval': datetime.datetime.strptime(data[3][1], "%Y-%m-%d %H:%M:%S").astimezone(LOCAL_TIMEZONE),
        'count_stops': int(data[4][1]),
        'move_time': construct_delta_time(data[5][1]),
        'millage': float(data[6][1][:-3]),
        'avg_speed': int(data[9][1][:-5]),
        'max_speed': int(data[10][1][:-5]),
        'stop_time': construct_delta_time(data[13][1]),
        'parking_count': int(data[14][1]),
    }


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


def convert_row_trip(row):
    return convert_row_trip_c(row['c'])


def convert_row_stop(row):
    return convert_row_stop_c(row['c'])


def convert_row_stop_c(row):
    return {
        'num': int(row[0]),
        'start_time': datetime.datetime.fromtimestamp(row[1]['v']).astimezone(LOCAL_TIMEZONE),
        'position': (float(row[1]['y']), float(row[1]['x'])),
        'end_time': datetime.datetime.fromtimestamp(row[2]['v']).astimezone(LOCAL_TIMEZONE),
        'time': construct_delta_time(row[3]),
    }


def convert_row_trip_c(row):
    return {
        'num': row[0],
        'start_time': datetime.datetime.fromtimestamp(row[1]['v']).astimezone(LOCAL_TIMEZONE),
        'start_position': (float(row[2]['y']), float(row[2]['x'])),
        'end_time': datetime.datetime.fromtimestamp(row[3]['v']).astimezone(LOCAL_TIMEZONE),
        'end_position': (float(row[4]['y']), float(row[4]['x'])),
        'time': construct_delta_time(row[5]),
        'millage': float(row[6][:-3]),
        'avg_speed': int(row[9][:-5]),
        'max_speed': int(row[10]['t'][:-5]),
        'max_speed_point': (float(row[10]['x']), float(row[10]['y']))
    }


def convert_position(position_struct):
    if position_struct:
        return {
            'time': datetime.datetime.fromtimestamp(position_struct['t'], LOCAL_TIMEZONE),
            'y': position_struct['y'],
            'x': position_struct['x'],
            'altitude': position_struct['z'],
            'speed': position_struct['s'],
            'course': position_struct['c'],
            'satellite': position_struct['sc'],
        }
    else:
        return None


def convert_table_rows(table_data, converters=None):
    converters = converters or {
        'unit_stops': convert_row_stop,
        'unit_trips': convert_row_trip,
    }
    table_name = table_data['header']['name']
    table_label = table_data['header']['label']
    rows = table_data['header']['rows']
    result = {
        'name': table_name,
        'label': table_label,
        'count': rows,
        'rows': [],
    }
    converter = converters.get(table_name, None)
    if converter:
        result['rows'] = [converter(row) for row in table_data['rows']]
    else:
        result['rows'] = table_data['rows']
    return result


def date_to_timestamp(dt: datetime.datetime, tzinfo=LOCAL_TIMEZONE):
    epoch = datetime.datetime(1970, 1, 1, tzinfo=tzinfo)
    timestamp = (dt - epoch) / datetime.timedelta(seconds=1)
    return timestamp


def date_to_int_timestamp(dt: datetime.datetime, tzinfo=LOCAL_TIMEZONE, use_correction=True):
    if use_correction:
        epoch = datetime.datetime(1970, 1, 1, tzinfo=tzinfo)
    else:
        epoch = datetime.datetime(1970, 1, 1, tzinfo=UTC_TIMEZONE)
    integer_timestamp = (dt.astimezone(datetime.timezone.utc) - epoch) // datetime.timedelta(seconds=1)
    return integer_timestamp


def date_to_correct_time(day: datetime.date, tzinfo=LOCAL_TIMEZONE, use_correction=True):
    return date_to_int_timestamp(datetime.datetime.combine(day, datetime.datetime.min.time()), tzinfo, use_correction)


def construct_delta_time(delta_time: str):
    return datetime.datetime.strptime(delta_time, "%H:%M:%S") - datetime.datetime(1900, 1, 1)
