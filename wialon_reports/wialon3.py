import datetime

from CarRentSystem import settings
from wialon_reports.WialonReporter import WialonReporter, convert_row, convert_row_trip, LOCAL_TIMEZONE
import environ

root = environ.Path(__file__)
env = environ.Env()
environ.Env.read_env()  # reading .env file

if __name__ == '__main__':
    api_key = env.str('WIALON_KEY')
    wialon = WialonReporter(api_key)

    wialon_obj_list = wialon.get_monitoring_objects()
    for wialon_obj in wialon_obj_list:
        print(wialon_obj)

    print(wialon.get_reports_list())


    # print(wialon.get_monitoring_objects_position())
    # print(wialon.get_objects_position(6753))

    def check_time(datetime_value: datetime) -> bool:
        if datetime_value.weekday() in [0, 1, 2, 3, 4] and (
                19 > datetime_value.time().hour > 8):
            return False
        else:
            print(datetime_value.strftime('%A %d/%m/%Y %H:%M:%S %w'))
            return True


    # report_id = 6827 NKT
    report_id = 112198
    # object_id = 6753
    object_id = 112171
    # for table, rows in wialon.get_report(report_id, 1, object_id, datetime.datetime(year=2022, month=1, day=13),
    #                                      datetime.datetime(year=2022, month=1, day=14), 1):
    #     print(table['label'])
    #     print(table['header'])
    #     for row in rows:
    #         print(row)
    #         row_data = convert_row_trip(row['c'])
    #     #     if check_time(row_data['start_time']) or check_time(row_data['end_time']):
    #     #         print(row_data)
    reports = wialon.get_report_sub_lists(report_id, 1, object_id,
                                          datetime.datetime(year=2022, month=1, day=13, tzinfo=LOCAL_TIMEZONE),
                                          datetime.datetime(year=2022, month=1, day=14, tzinfo=LOCAL_TIMEZONE), [0, 1])
    print(reports)
