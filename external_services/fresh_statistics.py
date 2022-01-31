import datetime

from argument_parser import parse_args
from django_common.django_native_execute import execute_code_in_django


def fresh_statistics_on_range(start_date: datetime.date = datetime.date.today() - datetime.timedelta(days=1),
                              days_count=7):
    from trip_stat.services.statisrics_service import Statistics

    # Statistics.create_statistics((datetime.datetime.now().date() - datetime.timedelta(days=1)))
    # # Statistics.create_statistics(datetime.datetime.strptime('16.10.2021', '%d.%m.%Y'))
    #
    stat_date = start_date - datetime.timedelta(days=(days_count-1))
    for i in range(days_count):
        print('Fresh ', stat_date)
        Statistics.create_statistics(stat_date)
        stat_date += datetime.timedelta(days=1)


if __name__ == '__main__':
    start_date, days, path = parse_args('Fresh Statistics')
    execute_code_in_django(lambda: fresh_statistics_on_range(start_date, days))
