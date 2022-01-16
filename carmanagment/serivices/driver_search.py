from datetime import datetime

from carmanagment.models import Car, CarSchedule, DriversSchedule, CarsInOperator


def get_car_current_driver(car: Car, current_date: datetime):
    if car:
        car_in_rent = CarSchedule.get_object_from_date(car, current_date)
        if car_in_rent and car_in_rent.driver:
            return car_in_rent.driver
        driver_schedule = DriversSchedule.get_driver(car, current_date)
        if driver_schedule and driver_schedule.driver:
            return driver_schedule.driver
        try:
            cars_operator = CarsInOperator.objects.filter(car=car).first()
            if cars_operator:
                return cars_operator.driver
        except CarsInOperator.DoesNotExist:
            pass
    return None
