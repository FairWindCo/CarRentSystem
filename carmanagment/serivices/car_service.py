from django.utils.timezone import now

from balance.services import Balance
from carmanagment.models import Investor, CarModel, Car, InvestmentCarBalance


class CarCreator:
    @staticmethod
    def add_new_car(investor: Investor, model: CarModel, car_plate: str, year: int, mileage_at_start: int,
                    start_amount: int) -> Car:
        return CarCreator.add_new_car_from_id(name=car_plate, year=year, mileage_at_start=mileage_at_start,
                                              start_amount=start_amount,
                                              model_id=model.pk, investor_id=investor.pk)

    @staticmethod
    def add_new_car_from_id(investor_id: int, model_id: int, car_plate: str, year: int, mileage_at_start: int,
                            start_amount: int, **kwargs) -> Car:
        car = Car(name=car_plate, year=year, mileage_at_start=mileage_at_start, control_mileage=mileage_at_start,
                  model_id=model_id, car_investor_id=investor_id)
        car.investment = InvestmentCarBalance(name=car_plate, create_date=now().date())
        car.investment.save()
        car.save()
        Balance.form_transaction(Balance.DEPOSIT, [
            (car.investment, None, start_amount * 100, 'Инвестиция')
        ], f'Включение авто {car_plate} {start_amount}$')
        return car