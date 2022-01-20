import datetime


def current_date(timezone=datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo):
    return datetime.datetime.now(timezone).date()


def parse_args(title):
    import argparse

    parser = argparse.ArgumentParser(description=title)
    parser.add_argument('--start', type=str,
                        default=(current_date() - datetime.timedelta(days=1)).__str__(),
                        required=False)
    parser.add_argument('--days', type=int, default=7, required=False)
    parser.add_argument('--path', type=str, default=None, required=False)
    parser.add_argument('--dformat', type=str, default='%Y-%m-%d', required=False)
    args = parser.parse_args()

    try:
        start_date = datetime.datetime.strptime(args.start, args.dformat).date()
    except ValueError:
        position = int(args.start)
        start_date = datetime.date.today() - datetime.timedelta(days=position)
    print('Start date', start_date)
    return start_date, args.days, args.path
