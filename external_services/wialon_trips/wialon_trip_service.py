import datetime

from external_services.argument_parser import parse_args
from external_services.django_common.django_native_execute import execute_code_in_django
from wialon_reports.WialonReporter import WialonReporter


def get_wialon_trip(
        last_day: datetime.date = datetime.date.today() - datetime.timedelta(days=1),
        day_count=1, report_id=112198, show_info=False, cache_path=None):
    from CarRentSystem import settings
    from carmanagment.models import Car
    from carmanagment.models import WialonDayStat, WialonTrip
    wialon_api_key = settings.WIALON_KEY
    wialon = WialonReporter(wialon_api_key)
    if show_info:
        print(wialon.get_monitoring_objects())
        print(wialon.get_reports_list())

    stat_date = last_day - datetime.timedelta(days=day_count)
    for i in range(day_count):
        cars_in_wailon = Car.objects.filter(wialon_id__isnull=False).all()
        start_time = datetime.datetime.combine(stat_date, datetime.datetime.min.time())
        for car in cars_in_wailon:
            reports = wialon.get_report_sub_lists_cached(report_id, 1, car.wialon_id,
                                                         start_time,
                                                         start_time + datetime.timedelta(days=1),
                                                         ['unit_trips'], cache_path=cache_path
                                                         )
            WialonDayStat.construct_from_dict(reports['summary'], car)
            if reports['tables']:
                WialonTrip.construct_from_rows(reports['tables'][0]['rows'], car)
        stat_date += datetime.timedelta(days=1)


if __name__ == '__main__':
    start_date, days, _ = parse_args('Get car data from Uklon')
    execute_code_in_django(lambda: get_wialon_trip(last_day=start_date, day_count=days, show_info=True))
