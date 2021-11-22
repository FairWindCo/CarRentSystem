import time
from datetime import datetime, timedelta

import environ
import requests
from django.utils import timezone
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


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

    def get_day_rides(self, day=None, vehicle_id: str = None, limit=None):
        if day is None:
            day = timezone.now()
        start_time = int(time.mktime(day.date().timetuple()))
        end_time = int(time.mktime((day + timedelta(days=1)).timetuple()))
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
                            response.append(trip)
                        else:
                            next_iteration = False
                    if next_iteration:
                        next_iteration = ('hasNext' in result and result['hasNext'])
                else:
                    break
            else:
                break
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
    print(uklon.get_day_rides())

    current_date = timezone.now()
    yesterday = current_date - timedelta(days=2)
    rides = uklon.get_day_rides(yesterday)

    for ride in rides:
        print(datetime.fromtimestamp(ride['pickup_time']))

    print(uklon.logout())

# https://partner.uklon.com.ua/partner/finances/search?page=1&pageSize=20&startDate=1631480400&endDate=1631739600
