from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

import data
import settings
from module import selectors, data_base, user_agents
from settings import Subscribe, StartSettings


from data import my_ip

import random
import time
import json


class BaseClass:
    def __init__(self):
        self.account_data = {
            'timer': 0,
            'proxy': True,
            'headless': True,
            'load_strategy': True,
        }

        self.browser = None

        self.count_limit = None
        self.subscribes = None
        self.count_iteration = 0
        self.count = 0
        self.cycle = 0

    parameters = {
        'sub': 'subscribe',
        'uns': 'unsubscribe',
        'fil': 'filter',
        'par': 'parce',
        'test': 'test',
        'ignore_list_path': 'ignore_list.txt',
        'parce_url_path': 'url_lists/subscribers_urls.txt',
        'non_filtered_path': 'non_filtered/subscribers_urls.txt',
        'filtered_path': 'filtered/subscribers_urls.txt',
    }

    def input_mode_and_set_working_parameters(self):
        user_input = input('Укажите режим работы (-параметры): ')
        self.account_data['WORK_MODE'] = BaseClass.parameters[user_input.split(' ')[0]]
        self.set_working_parameters(user_input)

    def set_working_parameters(self, user_input):
        user_input = f'{user_input} {settings.StartSettings.default_parameters}'
        for param in user_input.split(' '):
            if '-p' in param:
                self.account_data['proxy'] = not self.account_data['proxy']
            elif '-h' in param:
                self.account_data['headless'] = not self.account_data['headless']
            elif '-e' in param:
                self.account_data['load_strategy'] = not self.account_data['load_strategy']
            elif '-t' in param:
                self.account_data["timer"] = int(param.split('-t')[1].split(' ')[0])
            elif '-nonfilt' in user_input:
                self.parameters['filtered_path'] = self.parameters['non_filtered_path']

    def set_browser_parameters(self):
        self.account_data['chrome_option'] = webdriver.ChromeOptions()
        self.account_data['chrome_option'].add_argument(
            "--disable-blink-features=AutomationControlled")  # -webdriver mode
        self.account_data['chrome_option'].add_argument('--log-level=3')
        self.account_data['chrome_option'].add_argument('--ignore-certificate-errors-spki-list')
        self.account_data['chrome_option'].add_experimental_option('excludeSwitches', ['enable-logging'])
        if self.account_data['headless'] is True:
            self.account_data['chrome_option'].add_argument("--headless")
        if self.account_data['proxy'] is True:
            self.account_data['chrome_option'].add_argument(f'--proxy-server={data.proxy_list}')
        if self.account_data['load_strategy'] is True:
            self.account_data['chrome_option'].page_load_strategy = 'eager'

    def get_accounts_list(self):
        match self.account_data['WORK_MODE']:
            case 'subscribe' | 'unsubscribe' | 'test':
                accounts_key_number_list = list()
                account = input('Введите ID аккаунта: ')
                accounts_key_number_list.append(account)
                return accounts_key_number_list
            case 'parce' | 'filter':
                accounts_key_number_list = data_base.get_accounts_id_on_status('bot')
                random.shuffle(accounts_key_number_list)
                return accounts_key_number_list
            case _:
                raise Exception('Неизвестный режим работы, не могу установить маску аккаунта.')

    def set_account_parameters_by_db(self, account_id):
        self.account_data.update(data_base.get_account_field_data(account_id))

    def get_user_agent(self, account_id):
        user_agent_of_account = self.account_data['user_agent']
        if user_agent_of_account is not None:
            user_agent_of_account = f'user-agent={user_agent_of_account}'
        else:
            new_user_agent = random.choice(user_agents.user_agents)
            data_base.set_value_user_agent_field(account_id, new_user_agent)
            user_agent_of_account = f'user-agent={new_user_agent}'
            print(f'Присвоен новый UserAgent: {new_user_agent}')
        self.account_data['chrome_option'].add_argument(user_agent_of_account)

    def get_link(self, locator):
        item = self.search_element(locator, type_wait=ec.presence_of_element_located, timeout=10)
        url = item.get_attribute('src')
        return url

    def compare_my_ip_and_base_ip(self):
        pre = self.search_element(selectors.Technical.info_field_of_ip_address,
                                  type_wait=ec.presence_of_element_located
                                  ).text
        actual_ip = json.loads(pre)['ip']
        if actual_ip in my_ip:
            raise ConnectionError('При подключении через прокси зафиксирован "родной" IP-адрес.')

    def input_username_and_userpass(self):
        username_input = self.search_element(selectors.Login.username)
        username_input.clear()
        username_input.send_keys(self.account_data["user_name"])

        password_input = self.search_element(selectors.Login.password)
        password_input.clear()
        password_input.send_keys(self.account_data["user_pass"])
        password_input.send_keys(Keys.ENTER)

    def search_element(self, locator, timeout=StartSettings.web_driver_wait, type_wait=ec.element_to_be_clickable):
        return WebDriverWait(self.browser, timeout).until(type_wait(locator))

    def search_elements_on_tag(self, ignore=None):
        list_urls = set()
        while True:
            try:
                self.search_element(selectors.Technical.button_subscribe_into_followers_list_div_block)
                tags = self.browser.find_elements(*selectors.Technical.tag_a)
                for public_block in tags:
                    try:
                        profile_url = public_block.get_attribute('href')
                        len_user_url = len(profile_url.split('/'))  # у ссылки на профиль равен пяти.
                        if len_user_url == 5 \
                                and 'www.instagram.com' in profile_url \
                                and self.account_data["user_name"] not in profile_url \
                                and 'explore' not in profile_url \
                                and ignore not in profile_url:
                            list_urls.add(profile_url)
                    except AttributeError:
                        print('[AttributeError in search_elements_on_tag]', end=' ')
                return list_urls

            except StaleElementReferenceException as ex:
                print(ex)
                continue

    def scrolling_div_block(self, count):
        scroll_block = self.search_element(selectors.UserPage.followers_list_div_block,
                                           type_wait=ec.presence_of_element_located)
        for i in range(count):
            self.browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_block)
            for _ in range(2):
                self.search_element(selectors.UserPage.followers_list_progress_bar_icon,
                                    type_wait=ec.invisibility_of_element_located,
                                    timeout=10)
                time.sleep(0.5)

    def set_count_limit_for_subscribe(self):
        self.count_limit = Subscribe.subscribe_limit_stop - self.subscribes
