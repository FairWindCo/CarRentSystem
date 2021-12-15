import os
import pickle
import time
from datetime import datetime, timedelta, timezone

import environ
import requests
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo

class UklonTaxiService:
    base_url = 'https://partner.uklon.com.ua/'
    api = 'api/v1/'
    partner_api = ''
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}

    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password
        self.session = None
        self.rating = None
        self.drivers = {}
        self.cars = {}
        self.car_driver_datas = None
        self.uid = None
        self.balance = 0
        self.use_selenium = None

    @staticmethod
    def wait_page(browser, element_id):
        try:
            WebDriverWait(browser, 10).until(
                expected_conditions.presence_of_element_located((By.ID, element_id)))
            print("Page is ready!")
            return True
        except TimeoutException:
            print("Loading took too much time!")
            return False

    def connect(self, selenium=True):
        session = requests.Session()

        if selenium:
            from selenium import webdriver

            browser = webdriver.Firefox(executable_path=r'E:\Downloads\geckodriver-v0.30.0-win64\geckodriver.exe',
                                        firefox_profile='./profile')
            browser.get('https://partner.uklon.com.ua')
            self.use_selenium = browser
            user_field = browser.find_element_by_name('login')
            if user_field:
                user_field.send_keys(self.user)
                pass_field = browser.find_element_by_name('loginPassword')
                if pass_field:
                    pass_field.send_keys(self.password)
                    remembe_field = browser.find_element_by_xpath('//label[@for="rememberMe"]')
                    remembe_field.click()
                    time.sleep(3)
                    sendbtn = browser.find_element_by_name('Login')
                    if sendbtn:
                        sendbtn.click()
                        if not self.wait_page(browser, 'logoutForm'):
                            return False
                        browser.get('https://partner.uklon.com.ua/partner/vehicle')
                        if not self.wait_page(browser, 'logoutForm'):
                            return False
                        for cookie in browser.get_cookies():
                            session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
                            # c = {cookie['name']: cookie['value'], domain=cookie['domain']}
                            # session.cookies.update(c)
                            # print(c)
                        selenium_user_agent = browser.execute_script("return navigator.userAgent;")
                        app_uid = browser.execute_script('n=window.localStorage,r=n.getItem("app_uid");')
                        self.headers = {"user-agent": selenium_user_agent,
                                        'app_uid': app_uid,
                                        'Referer': 'https://partner.uklon.com.ua/'}
                        self.session = session
                        return True
            # session.cookies = cookies
        self.use_selenium = False
        json = {
            'login': self.user,
            'password': self.password,
            'persist': True
        }
        url = f'{self.base_url}{self.api}login'
        response = session.post(url, json=json, headers=self.headers)
        if response.status_code == 200:
            self.session = session
            return True
        # print(response.text, url, json)
        return False

    def _send_request(self, url: str = '/', method: str = 'POST',
                      json: dict = None,
                      data: dict = None,
                      params: dict = None,
                      debug=False, return_json=True) -> (bool, int, dict):
        if debug:
            print(url)
            print(self.headers)
            print(self.session.cookies)
        kwargs = {
            'headers': self.headers
        }
        if json:
            kwargs['json'] = json
        if data:
            kwargs['data'] = data
        if params:
            kwargs['params'] = params
        if self.session is not None:
            method = getattr(self.session, method.lower(), None)
            if method:
                response = method(url, **kwargs)

                if response.status_code == 200:
                    if return_json:
                        return True, response.status_code, response.json()
                    else:
                        return True, response.status_code, response.text
                else:
                    return False, response.status_code, {}
        return False, 0, {}

    def _send_api_request(self, endpoint: str = 'me', method: str = 'POST', api: str = '', json: dict = None,
                          data: dict = None, params=None, debug=False) -> dict:
        url = f'{self.base_url}{api}{endpoint}'
        _, _, obj = self._send_request(url, method, json, data, params, debug)
        return obj

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

    def get_ride_info(self, ride_id):
        # https://partner.uklon.com.ua/api/v1/driver/orders/e9da3779-ac15-4d06-8b1a-d823fb9d6d1a
        # return object like
        # {"uid":"e9da3779ac154d068b1ad823fb9d6d1a",
        # "fee_type":"mixed","cost":149,"cash_cost":94,"distance":7.01,
        # "pickup_time":1639171121,"add_conditions":[],"clients_comments":[null],"idle":0,"start_sector":"ПАНЬКОВЩИНА",
        # "end_sector":"НАУ","route":{"route_points":[{"address_name":"Світова (Жилянська вулиця, 74)","lat":50.43695,"lng":30.50221,"is_place":true,"atype":"geocode",
        # "type":"pickup"},{"address_name":"Вадима Гетьмана вулиця, 44","lat":50.43891,"lng":30.44536,"is_place":true,"atype":"geocode","type":"dropoff"}]},"route_legs":[[[30.50206,50.43687],[30.50258,50.43645],[30.50391,50.43544],[30.50485,50.43474],[30.5057,50.43459],[30.50595,50.43518],[30.50614,50.43572],[30.50644,50.43646],[30.50587,50.43653],[30.50562,50.4367],[30.50531,50.43694],[30.50305,50.43859],[30.50264,50.43895],[30.50176,50.43961],[30.50142,50.43985],[30.50123,50.43998],[30.49976,50.44107],[30.49973,50.44111],[30.49961,50.44122],[30.49698,50.44366],[30.49682,50.4438],[30.4959,50.44466],[30.49507,50.44547],[30.49454,50.44591],[30.49435,50.44592],[30.49413,50.44582],[30.49387,50.4457],[30.49349,50.44554],[30.49285,50.44529],[30.49272,50.44529],[30.49254,50.44533],[30.49236,50.44555],[30.49057,50.44616],[30.4889,50.44634],[30.48664,50.44625],[30.48568,50.44634],[30.48371,50.44661],[30.48274,50.44687],[30.47983,50.44743],[30.47946,50.44748],[30.47869,50.44759],[30.4782,50.44765],[30.47718,50.44777],[30.47622,50.44781],[30.47534,50.44785],[30.47311,50.4477],[30.47169,50.44748],[30.47035,50.4473],[30.46721,50.44671],[30.46704,50.44667],[30.46535,50.44635],[30.46378,50.446],[30.46329,50.44591],[30.46264,50.44582],[30.46186,50.4458],[30.46063,50.44584],[30.45315,50.44674],[30.45259,50.44666],[30.44841,50.44569],[30.44581,50.445],[30.44304,50.44431],[30.44084,50.44376],[30.44037,50.44384],[30.44052,50.44408],[30.44155,50.44437],[30.44182,50.44419],[30.44208,50.44336],[30.44218,50.44326],[30.44387,50.44072],[30.44325,50.44052],[30.44181,50.44022],[30.44187,50.44013],[30.44234,50.43951],[30.44316,50.43964],[30.44377,50.43948],[30.44389,50.43909],[30.44537,50.43897]]],"currency":"UAH","offer_accepted_at":1639170707,"completed_at":1639171644}

        res = self._send_api_request(endpoint=f'driver/orders/{ride_id}',
                                     method='GET', debug=False, api=self.api)
        print(res)
        if res['fee_type'] == 'mixed':
            return res['cost'], res['cash_cost']
        return res['cost'], 0

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
                                     method='GET', debug=False, api=self.api, params=params)
        return res

    def get_day_rides(self, day=None, vehicle_id: str = None, limit=None, cache_path = None):
        if day is None:
            day = datetime.now(LOCAL_TIMEZONE).date()

        file_path = None
        start_time = int(time.mktime(day.date().timetuple()))
        end_time = int(time.mktime((day.date() + timedelta(days=1)).timetuple()))
        # print(day.date(), start_time, end_time)
        if cache_path is not None:
            file_path = os.path.join(cache_path, f"uklon_{vehicle_id}_{day.strftime('%d-%m-%y')}.dat")
            # print(file_path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, "rb") as file:
                    return pickle.load(file)
        count = 0
        page = 1
        response = []
        next_iteration = True
        while next_iteration and (limit is None or count < limit):
            result = self.get_rides(start_time, end_time, vehicle_id=vehicle_id, page=page)
            if result:
                if 'collection' in result:
                    trips = result['collection']
                    page = page + 1
                    for trip in trips:
                        if end_time >= trip['pickup_time'] >= start_time:
                            if trip['status'] == 'completed':
                                if trip['payments']['fee_type'] == 'mixed':
                                    additional_many = self.get_ride_info(trip['uid'])
                                    trip['cash_many_info'] = additional_many[1]
                                    trip['pay_many_info'] = additional_many[0]
                                else:
                                    trip['cash_many_info'] = trip['cost'] if trip['payments'][
                                                                                 'fee_type'] == 'cash' else 0
                                    trip['pay_many_info'] = trip['cost']
                                    trip['timezone_time'] = trip['cost']
                                response.append(trip)
                        else:
                            next_iteration = False
                    if next_iteration:
                        next_iteration = ('hasNext' in result and result['hasNext'])
                else:
                    break
            else:
                break
        if response and cache_path is not None:
            if not os.path.exists('../UKLON'):
                os.mkdir('../UKLON')
            with open(file_path, "wb") as file:
                pickle.dump(response, file)
        return response

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
        res, _, _ = self._send_request(f'{self.base_url}account/logout', return_json=False)
        if self.use_selenium:
            self.use_selenium.close()
        return res


if __name__ == '__main__':
    env = environ.Env(
        # set casting, default value
        DEBUG=(bool, False)
    )
    environ.Env.read_env()
    user_name = env('UKLON_USER')
    user_pass = env('UKLON_PASS')
    # print(user_name, user_pass)
    uklon = UklonTaxiService(user_name, user_pass)
    uklon.use_selenium = False
    print(uklon.connect(selenium=False))
    print((uklon.get_my_info()))
    # print((uklon.get_self_driver_info()))
    # print((uklon.get_balance()))
    # print((uklon.driver_cars()))
    # print((uklon.get_partner_rating()))
    # print(uklon.rating)
    # print(uklon.get_partner_drivers_and_cars())
    # print(uklon.cars)
    # print(uklon.drivers)
    # print(uklon.get_rides())
    # print(uklon.get_day_rides())

    # current_date = timezone.now()
    # yesterday = current_date - timedelta(days=2)
    # rides = uklon.get_day_rides(yesterday)
    #
    # for ride in rides:
    #     print(datetime.fromtimestamp(ride['pickup_time']))
    current_date = datetime.now() - timedelta(days=2)
    start_day = current_date - timedelta(days=9)

    while start_day < current_date:
        rides = uklon.get_day_rides(start_day)

        for ride in rides:
            print(datetime.fromtimestamp(ride['pickup_time']))

        start_day += timedelta(days=1)

    print(uklon.logout())

# https://partner.uklon.com.ua/partner/finances/search?page=1&pageSize=20&startDate=1631480400&endDate=1631739600
