import pickle

from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as ec
from data import my_ip
from settings import Subscribe, StartSettings
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from module import message_text
from module import exception
from module.option import BotOption
from module.tools import Tools
from datetime import datetime
import traceback
import time
import json


class BaseClass:

    def __init__(self):
        self.account_option = BotOption()
        self.browser = None

        self.count_limit = None
        self.subscribes = None
        self.count_iteration = 0
        self.count = 0
        self.cycle = 0
        self.timer = 0

    def get_link(self, locator):
        item = self.search_element(locator, type_wait=ec.presence_of_element_located, timeout=10)
        url = item.get_attribute('src')
        return url

    def compare_my_ip_and_base_ip(self):
        pre = self.search_element((By.TAG_NAME, "body"), type_wait=ec.presence_of_element_located).text
        actual_ip = json.loads(pre)['ip']
        if actual_ip in my_ip:
            raise ConnectionError('При подключении через прокси зафиксирован "родной" IP-адрес.')

    def set_cookie(self):
        self.browser.delete_all_cookies()
        self.browser.refresh()
        self.cookie_accept()
        self.should_be_home_page()
        for cookie in pickle.load(open(f'data/cookies/{self.account_option.username}_cookies', 'rb')):
            self.browser.add_cookie(cookie)
        time.sleep(1)
        self.browser.refresh()

    def save_new_cookie(self):
        pickle.dump(self.browser.get_cookies(), open(f'data/cookies/{self.account_option.username}_cookies', 'wb'))

    def input_username_and_userpass(self):
        username_input = self.search_element((By.NAME, "username"))
        username_input.clear()
        username_input.send_keys(self.account_option.username)

        password_input = self.search_element((By.NAME, "password"))
        password_input.clear()
        password_input.send_keys(self.account_option.password)
        password_input.send_keys(Keys.ENTER)

    def search_element(self, locator, timeout=StartSettings.web_driver_wait, type_wait=ec.element_to_be_clickable):
        return WebDriverWait(self.browser, timeout).until(type_wait(locator))

    def tag_search(self, ignore=None):
        list_urls = set()
        while True:
            try:
                self.search_element((By.CSS_SELECTOR, 'div.Pkbci > button'))
                tags = self.browser.find_elements(By.TAG_NAME, 'a')
                for public_block in tags:
                    profile_url = public_block.get_attribute('href')
                    len_user_url = len(profile_url.split('/'))  # у ссылки на профиль равен пяти.
                    if len_user_url == 5 \
                            and 'www.instagram.com' in profile_url \
                            and self.account_option.username not in profile_url \
                            and 'explore' not in profile_url \
                            and ignore not in profile_url:
                        list_urls.add(profile_url)
                return list_urls

            except StaleElementReferenceException:
                print(StaleElementReferenceException)
                continue

    def scrolling_div_block(self, count):
        scroll_block = self.search_element((By.CSS_SELECTOR, 'div.RnEpo.Yx5HN > div > div > div> div.isgrP'),
                                           type_wait=ec.presence_of_element_located)
        for i in range(count):
            self.browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_block)
            self.search_element((By.CSS_SELECTOR, 'li div svg.By4nA'), timeout=10,
                                type_wait=ec.invisibility_of_element_located)
            time.sleep(0.5)
            self.search_element((By.CSS_SELECTOR, 'li div svg.By4nA'), timeout=10,
                                type_wait=ec.invisibility_of_element_located)
            time.sleep(0.5)

    def get_user_url_from_file(self, file_path, difference_ignore_list=True):
        try:
            if difference_ignore_list:
                user_list = Tools.difference_sets(file_path)
            else:
                user_list = []
                Tools.file_read(file_path, user_list)
            self.account_option.user_url = user_list.pop()
            Tools.file_write(file_path, user_list, operating_mode='w')
        except IndexError:
            raise exception.BotFinishTask(
                self.account_option,
                message_text.InformationMessage.task_finish)

    def return_amount_posts_subscribes_and_subscribers(self):
        dict_return = dict()
        try:
            subscriptions_field = self.search_element((By.CSS_SELECTOR, 'li:nth-child(3) > a > div > span.g47SY'),
                                                      type_wait=ec.presence_of_element_located, timeout=3)

            dict_return['subs'] = int(
                subscriptions_field.text.replace(" ", "").replace(',', ''))
        except TimeoutException:
            dict_return['subs'] = 0

        try:
            subscribe_field = self.search_element((By.CSS_SELECTOR, 'li:nth-child(2) > a > div > span.g47SY'),
                                                  type_wait=ec.presence_of_element_located, timeout=3)
            if ',' in subscribe_field.text:
                dict_return['follow'] = int(
                    subscribe_field.text.replace(" ", "").replace(',', '').replace('тыс.', '00').replace('млн',
                                                                                                         '00000'))
            else:
                dict_return['follow'] = int(
                    subscribe_field.text.replace(" ", "").replace('тыс.', '000').replace('млн', '000000'))
        except TimeoutException:
            dict_return['follow'] = 1

        post_number_field = self.search_element((By.CSS_SELECTOR, 'li:nth-child(1) > div > span.g47SY'),
                                                type_wait=ec.presence_of_element_located)
        dict_return['posts'] = int(
            post_number_field.text.replace(" ", "").replace(',', '').replace('тыс.', '000').replace('млн', '000000'))

        return dict_return

    def set_count_limit_for_subscribe(self):
        if self.account_option.second_mode == BotOption.parameters['short']:
            self.count_limit = Subscribe.subscribe_limit_stop
        else:
            self.count_limit = Subscribe.subscribe_limit_stop - self.subscribes

    def standard_exception_handling(self):

        self.save_log_exception()
        exception_name = str(type(self.account_option.exception)).split("'")[1].split('.')[-1]
        if self.account_option.mode == self.account_option.parameters['fil'] \
                and isinstance(self.account_option.exception, KeyError):
            raise exception.BotFinishTask(
                self.account_option,
                message_text.FilterMessage.list_empty)
        print(f'\nИсключение обработано и добавлено в лог: {self.account_option.mode}/{exception_name}')

    def save_log_exception(self):
        exception_name = str(type(self.account_option.exception)).split("'")[1].split('.')[-1]
        path = f'logs/{self.account_option.mode}/{exception_name}.txt'

        date = datetime.now().strftime("%d-%m %H:%M:%S")
        exception_text = traceback.format_exc()
        log_text = f'{date}\n{exception_text}\n\n'

        Tools.file_write(path, log_text)

        if 'CONNECTION_FAILED' in exception_text:
            timeout = StartSettings.err_proxy_timeout
            error_name = exception_text.split('net::')[1].split('\n')[0]
            print(f'{date.split(" ")[1]} -- {self.account_option.mode} >> {error_name}. ',
                  f'Запись добавлена в лог. Таймаут {timeout} секунд.')
            time.sleep(timeout)

    def shaffle_file_for_task(self):
        if self.account_option.mode == BotOption.parameters['par']:
            Tools.shaffle_file(BotOption.parameters['parce_url_path'])
            print(f'Файл {BotOption.parameters["parce_url_path"]} - перемешан.')
        elif self.account_option.mode == BotOption.parameters['fil']:
            Tools.shaffle_file(BotOption.parameters['non_filtered_path'])
            print(f'Файл {BotOption.parameters["non_filtered_path"]} - перемешан.')
        else:
            raise Exception('Неизвестный режим в методе "shaffle_file_for_task".')




