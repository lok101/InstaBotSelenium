from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as ec
from module import message_text, exception, selectors
from settings import Subscribe, StartSettings
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from module.option import BotOption
from module.tools import Tools
from data import my_ip
import pickle
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

    def set_cookie(self):
        self.browser.delete_all_cookies()
        self.browser.refresh()
        self.cookie_accept()
        self.should_be_login_page()
        for cookie in pickle.load(
                open(f'data/cookies_and_userAgent/{self.account_option.account_data["user_name"]}_cookies', 'rb')):
            self.browser.add_cookie(cookie)
        time.sleep(1)
        self.browser.refresh()

    def save_new_cookie(self):
        pickle.dump(self.browser.get_cookies(),
                    open(f'data/cookies_and_userAgent/{self.account_option.account_data["user_name"]}_cookies', 'wb'))

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
                print('============================')
                print(tags)
                print('============================')
                for public_block in tags:
                    profile_url = public_block.get_attribute('href')
                    print(f'public_block: {public_block}')
                    print(f'profile_url: {profile_url}')
                    len_user_url = len(profile_url.split('/'))  # у ссылки на профиль равен пяти.
                    if len_user_url == 5 \
                            and 'www.instagram.com' in profile_url \
                            and self.account_option.account_data["user_name"] not in profile_url \
                            and 'explore' not in profile_url \
                            and ignore not in profile_url:
                        list_urls.add(profile_url)
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
            subscriptions_field = self.search_element(selectors.UserPage.subscriptions,
                                                      type_wait=ec.presence_of_element_located,
                                                      timeout=3)

            dict_return['subs'] = int(
                subscriptions_field.text.replace(" ", "").replace(',', ''))
        except TimeoutException:
            dict_return['subs'] = 0

        try:
            followers_field = self.search_element(selectors.UserPage.followers,
                                                  type_wait=ec.presence_of_element_located,
                                                  timeout=3)
            if ',' in followers_field.text:
                dict_return['follow'] = int(
                    followers_field.text.replace(" ", "").replace(',', '').replace('тыс.', '00').replace('млн',
                                                                                                         '00000'))
            else:
                dict_return['follow'] = int(
                    followers_field.text.replace(" ", "").replace('тыс.', '000').replace('млн', '000000'))
        except TimeoutException:
            dict_return['follow'] = 1

        post_number_field = self.search_element(selectors.UserPage.posts, type_wait=ec.presence_of_element_located)
        dict_return['posts'] = int(
            post_number_field.text.replace(" ", "").replace(',', '').replace('тыс.', '000').replace('млн', '000000'))

        return dict_return

    def set_count_limit_for_subscribe(self):
        if self.account_option.second_mode == BotOption.parameters['short']:
            self.count_limit = Subscribe.subscribe_limit_stop
        else:
            self.count_limit = Subscribe.subscribe_limit_stop - self.subscribes

    def cookie_accept(self):
        button_cookie_accept = self.search_element(selectors.Login.button_cookie_accept)
        button_cookie_accept.click()
        time.sleep(2)
