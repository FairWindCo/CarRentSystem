from datetime import datetime

import environ
import requests


class UklonTaxiService:
    base_url = 'https://partner.uklon.com.ua/'
    api = 'api/v1/'
    partner_api = ''
    headers = {'user-agent': 'my-app/0.0.1'}

    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password
        self.session = None
        self.rating = None
        self.drivers = {}
        self.cars = {}
        self.car_driver_datas = None

    def connect(self):
        if self.session is not None:
            self.logout()
        session = requests.Session()
        response = session.post(f'{self.base_url}{self.api}login', json={
            'login': self.user,
            'password': self.password,
            'persist': True
        }, headers=self.headers)
        if response.status_code == 200:
            self.session = session
            return True
        return False

    def _send_api_request(self, endpoint: str = 'me', method: str = 'POST', api: str = '', json: dict = None,
                          data: dict = None, debug=False) -> dict:
        url = f'{self.base_url}{api}{endpoint}'
        if debug:
            print(url)
        if self.session is not None:
            if method == 'POST':
                response = self.session.post(url, data=data, json=json,
                                             headers=self.headers)
            else:
                response = self.session.get(url, params=data, json=json,
                                            headers=self.headers)
            if response.status_code == 200:
                return response.json()
        return {}

    def get_uid__balance(self, uid):
        result = {}
        if uid:
            result = self._send_api_request(endpoint=f'drivers/{uid}/uwallet/balance', method='GET', api=self.api)
        return result

    def get_balance(self):
        result = {}
        if self.uid:
            result = self.get_uid__balance(self.uid)
            if result:
                self.balance = result['balance']
        return result

    def driver_cars(self):
        result = {}
        if self.uid:
            result = self._send_api_request(endpoint=f'drivers/{self.uid}/vehicle', method='GET', api=self.api)
        return result

    def get_my_info(self):
        result = self._send_api_request(endpoint='me', method='GET', api=self.api)
        if result:
            self.uid = result['uid']
        return result

    def get_self_driver_info(self):
        result = self._send_api_request(endpoint='driver/me', method='GET', api=self.api)
        if result:
            self.uid = result['uid']
        return result

    def get_partner_rating(self):
        res = self._send_api_request(endpoint='rating', method='GET', api='partner/home/')
        if res:
            self.rating = {
                'rating': res['Rating'],
                'marks': res['MarksCount'],
                'last_update': datetime.fromtimestamp(int(res['UpdatedAt'])),
            }
        return res

    def get_rides(self, from_time=None, to_time=None, driver_id: str = None, vehicle_id: str = None, page: int = 1,
                  size: int = 50):
        params = {
            'page': page,
            'pageSize': size
        }
        if from_time is not None:
            params['from'] = from_time
        if to_time is not None:
            params['to'] = to_time
        if driver_id is not None:
            params['driverId'] = driver_id
        if vehicle_id is not None:
            params['vehicleId'] = vehicle_id

        res = self._send_api_request(endpoint=f'fleets/{self.uid}/history-rides',
                                     method='GET', debug=True, api=self.api, data=params)
        return res

    def process_car_driver_data(self, car_driver_data):
        self.drivers.clear()
        self.cars.clear()
        for car_driver in car_driver_data:
            phone = car_driver['driver']['phone']
            self.drivers[phone] = {
                'uid': car_driver['driver']['uid'],
                'rating': car_driver['driver']['rating'],
                'signal': car_driver['driver']['signal'],
                'phone': car_driver['driver']['phone'],
                'marks_count': car_driver['driver']['marks_count'],
            }
            license_plate = car_driver['vehicle']['license_plate']
            self.cars[license_plate] = {
                'uid': car_driver['vehicle']['uid'],
                'license_plate': car_driver['vehicle']['license_plate'],
                'body_type': car_driver['vehicle']['body_type'],
                'color': car_driver['vehicle']['color'],
                'comfort_level': car_driver['vehicle']['comfort_level'],
                'make': car_driver['vehicle']['make'],
                'model': car_driver['vehicle']['model'],
                'year': car_driver['vehicle']['year'],
            }

    def get_partner_drivers_and_cars(self):
        res = self._send_api_request(endpoint=f'fleets/{self.uid}/driver-accounts',
                                     method='GET', api=self.api)
        if res:
            self.car_driver_datas = res
            self.process_car_driver_data(res)
        return res

    def logout(self):
        if self.session is not None:
            response = self.session.post(f'{self.base_url}account/logout')
            if response.status_code == 200:
                self.session = None
                return True
        return False


if __name__ == '__main__':
    env = environ.Env(
        # set casting, default value
        DEBUG=(bool, False)
    )
    environ.Env.read_env()
    user_name = env('UKLON_USER')
    user_pass = env('UKLON_PASS')
    uklon = UklonTaxiService(user_name, user_pass)
    print(uklon.connect())
    print((uklon.get_my_info()))
    print((uklon.get_self_driver_info()))
    print((uklon.get_balance()))
    print((uklon.driver_cars()))
    print((uklon.get_partner_rating()))
    print(uklon.rating)
    print(uklon.get_partner_drivers_and_cars())
    print(uklon.cars)
    print(uklon.drivers)
    print(uklon.get_rides())
    print(uklon.logout())


#https://partner.uklon.com.ua/partner/finances/search?page=1&pageSize=20&startDate=1631480400&endDate=1631739600