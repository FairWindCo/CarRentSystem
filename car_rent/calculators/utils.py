from math import floor


def float_round(num, places=0, direction=floor):
    return direction(num * (10 ** places)) / float(10 ** places)
