import datetime

from wialon_reports.WialonReporter import WialonReporter, convert_row

if __name__ == '__main__':
    wialon = WialonReporter('db69899bb2d08b9d3804ffd183ff20ac1164DB3636204B7114E158B9152BB1A9E4B414A1')
    print(wialon.get_monitoring_objects())
    print(wialon.get_reports_list())
    print(wialon.get_monitoring_objects_position())
    print(wialon.get_objects_position(6753))

    def check_time(datetime_value: datetime) -> bool:
        if datetime_value.weekday() in [0, 1, 2, 3, 4] and (
                19 > datetime_value.time().hour > 8):
            return False
        else:
            print(datetime_value.strftime('%A %d/%m/%Y %H:%M:%S %w'))
            return True


    for table, rows in wialon.get_report(6827, 1, 6753, datetime.datetime(year=2021, month=8, day=1),
                                         datetime.datetime(year=2021, month=8, day=30), 0):
        print(table['label'])
        print(table['header'])
        for row in rows:
            row_data = convert_row(row['c'])
            if check_time(row_data['start_time']) or check_time(row_data['end_time']):
                print(row_data)
