from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

from module import selectors
from settings import Subscribe, StartSettings
from module.option import BotOption
from data import my_ip

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
        username_input.send_keys(self.account_option.account_data["user_name"])

        password_input = self.search_element(selectors.Login.password)
        password_input.clear()
        password_input.send_keys(self.account_option.account_data["user_pass"])
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
                                and self.account_option.account_data["user_name"] not in profile_url \
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
        if self.account_option.second_mode == BotOption.parameters['short']:
            self.count_limit = Subscribe.subscribe_limit_stop
        else:
            self.count_limit = Subscribe.subscribe_limit_stop - self.subscribes
