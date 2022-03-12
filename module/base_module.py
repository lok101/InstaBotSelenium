from module.exception_module import PageLoadingError, ActivBlocking, LoginError, PageNotAvailable, UserPageNotExist, \
    VerificationError, BotFinishTask
from module.message_text_module import InformationMessage, LoginErrorMessage, FilterMessage
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as ec
from settings import Subscribe, StartSettings, Unsubscribe
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from module.option import BotOption
from module.tools import Tools
from datetime import datetime
from data import my_ip
import traceback
import pickle
import random
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

    def cookie_login(self):
        self.browser.delete_all_cookies()
        for cookie in pickle.load(open(f'data/cookies/{self.account_option.username}_cookies', 'rb')):
            self.browser.add_cookie(cookie)
        time.sleep(1)
        self.browser.refresh()
        self.should_be_verification_form()
        self.should_be_login_button()
        print('Залогинился через cookies.')

    def not_cookie_login(self):
        username_input = self.search_element((By.NAME, "username"))
        username_input.clear()
        username_input.send_keys(self.account_option.username)

        password_input = self.search_element((By.NAME, "password"))
        password_input.clear()
        password_input.send_keys(self.account_option.password)

        password_input.send_keys(Keys.ENTER)
        time.sleep(5)
        self.should_be_login_form_error()
        self.should_be_verification_form()
        self.should_be_login_button()

        # сохраняем cookies
        pickle.dump(self.browser.get_cookies(), open(f'data/cookies/{self.account_option.username}_cookies', 'wb'))
        print(f'Залогинился и создал cookies ===> data/cookies/{self.account_option.username}_cookies.')

    def check_proxy_ip(self):
        self.browser.get("https://api.myip.com/")
        pre = self.search_element((By.TAG_NAME, "body"), type_wait=ec.presence_of_element_located).text
        actual_ip = json.loads(pre)['ip']
        if actual_ip in my_ip:
            raise ConnectionError('При подключении через прокси зафиксирован "родной" IP-адрес.')
        date = datetime.now().strftime("%H:%M:%S")
        print(f'{date} Подключение через прокси: {actual_ip}', end=' ===> ')

    def get_link(self, locator):
        item = self.search_element(locator, type_wait=ec.presence_of_element_located, timeout=10)
        url = item.get_attribute('src')
        return url

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

    def return_number_posts_subscribe_and_subscribers(self):
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

    def set_user_url_from_file(self, file_path, difference_ignore_list=True):
        try:
            if difference_ignore_list:
                user_list = Tools.difference_sets(file_path)
            else:
                user_list = []
                Tools.file_read(file_path, user_list)
            self.account_option.user_url = user_list.pop()
            Tools.file_write(file_path, user_list, operating_mode='w')
        except IndexError:
            raise BotFinishTask(self.account_option, InformationMessage.task_finish)

    def print_statistics_on_filtration(self):
        non_filtered, filtered = set(), set()
        self.set_user_url_from_file((BotOption.parameters["non_filtered_path"]))    # вычитает из файла игнор лист
        Tools.file_read((BotOption.parameters["non_filtered_path"]), non_filtered)
        Tools.file_read((BotOption.parameters["filtered_path"]), filtered)
        print(
            f'\nНе отфильтровано - {len(non_filtered)}.'
            f'\nГотовых - {len(filtered)}.',
            f'\nОтобрано в сессии - [{self.count}/{self.cycle * 50}].\n')
        self.cycle += 1

    def print_statistics_on_parce(self):
        non_filtered = set()
        Tools.file_read((BotOption.parameters["non_filtered_path"]), non_filtered)
        self.count_iteration += 1
        print(f'Успешно. Количество собранных пользователей: {len(non_filtered)}.')

    def get_users_url_for_parce(self):
        urls_public = []
        Tools.file_read((BotOption.parameters["parce_url_path"]), urls_public)
        self.count_limit = len(urls_public)
        if self.count_iteration >= self.count_limit:
            raise BotFinishTask(self.account_option, InformationMessage.task_finish)
        urls_public = urls_public[self.count_iteration:-1]
        return urls_public

    def press_to_subscribe_button(self):
        button = self.search_element((By.XPATH, '//button'))
        if 'подписаться' in button.text.lower():
            iteration_limit = 10
            iteration_count = 0
            while iteration_count < iteration_limit:
                iteration_count += 1
                button.click()
                time.sleep(random.randrange(Subscribe.min_timeout, Subscribe.max_timeout))
                self.should_be_subscribe_and_unsubscribe_blocking()
                Tools.file_write((BotOption.parameters["ignore_list_path"]), self.account_option.user_url)
                self.count_iteration += 1
                print('Успешно подписался.')
                break
        else:
            print('Кнопка не найдена.')
            Tools.file_write((BotOption.parameters["ignore_list_path"]), self.account_option.user_url)
            time.sleep(random.randrange(Subscribe.min_timeout, Subscribe.max_timeout))

    def check_limits_from_subscribe(self):
        if self.count_iteration % Subscribe.subscribe_in_session == 0 and self.count_iteration != 0:
            self.go_to_my_profile_page_and_set_subscribes_amount(end_str=' ')
            print(f'{datetime.now().strftime("%H:%M:%S")} Подписался на очередные',
                  f'{Subscribe.subscribe_in_session} пользователей. ',
                  f'Таймаут {Subscribe.sleep_between_iterations} минут.')
            time.sleep(Subscribe.sleep_between_iterations * 60)

    def press_to_unsubscribe_button_and_set_timeouts(self, user):
        user.find_element(By.TAG_NAME, "button").click()  # нажать кнопку отписки
        time.sleep(random.randrange(Unsubscribe.min_sleep, Unsubscribe.max_sleep))
        self.search_element((By.CSS_SELECTOR, "button.-Cab_")).click()  # нажать кнопку подтверждения
        self.should_be_subscribe_and_unsubscribe_blocking()
        self.count_iteration += 1
        print(
            f'{datetime.now().strftime("%H:%M:%S")} - {self.account_option.username} - ',
            f'[{self.count_iteration}/10] - Успешно отписался.')

    def go_to_user_page(self, end_str=' ===> '):
        self.browser.get(self.account_option.user_url)
        username = self.account_option.user_url.split("/")[-2]
        print(
            f'{datetime.now().strftime("%H:%M:%S")} - {self.account_option.username} - ',
            f'[{self.count_iteration + 1}/{self.count_limit}]',
            f'Перешёл в профиль: {username}', end=end_str)

        self.should_be_instagram_page()
        self.should_be_activity_blocking()
        self.should_be_user_page()
        self.should_be_verification_form()

    def go_to_my_profile_page_and_set_subscribes_amount(self, end_str='\n'):
        url = f'https://www.instagram.com/{self.account_option.username}/'
        self.browser.get(url)
        self.should_be_instagram_page()
        self.should_be_activity_blocking()
        self.should_be_verification_form()

        self.subscribes = self.return_number_posts_subscribe_and_subscribers()['subs']
        print(f"Количество подписок: {self.subscribes}", end=end_str)

    def set_count_limit_for_subscribe(self):
        if self.account_option.second_mode == BotOption.parameters['short']:
            self.count_limit = Subscribe.subscribe_limit_stop
        else:
            self.count_limit = Subscribe.subscribe_limit_stop - self.subscribes

    def should_be_user_page(self):
        while True:
            try:
                error_message = self.search_element((By.CSS_SELECTOR, 'div > div > h2'), timeout=1,
                                                    type_wait=ec.presence_of_element_located)
                if 'К сожалению, эта страница недоступна' in error_message.text:
                    raise UserPageNotExist(self.account_option, InformationMessage.page_not_exist)
                elif 'Это закрытый аккаунт' in error_message.text:
                    raise PageNotAvailable(self.account_option, FilterMessage.profile_closed)
                elif 'Вам исполнилось' in error_message.text:
                    raise PageNotAvailable(self.account_option, InformationMessage.check_age)
                else:
                    print('Неизвестное окно при вызове "should_be_user_page".')
                break

            except TimeoutException:
                break

            except StaleElementReferenceException:
                continue

    def should_be_home_page(self):
        try:
            self.search_element((By.NAME, "username"),
                                timeout=10, type_wait=ec.presence_of_element_located)
            print(f'Логин с аккаунта - {self.account_option.username}')
        except TimeoutException:
            raise LoginError(self.account_option, LoginErrorMessage.not_login_page)

    def should_be_verification_form(self):
        try:
            self.search_element((By.CSS_SELECTOR, 'div.ctQZg.KtFt3 > button > div'), timeout=2)
            raise VerificationError(self.account_option, LoginErrorMessage.verification_form)

        except TimeoutException:
            pass

    def should_be_login_form_error(self):
        try:
            element = self.search_element((By.CSS_SELECTOR, '#slfErrorAlert'),
                                          timeout=1, type_wait=ec.presence_of_element_located)
            if 'К сожалению, вы ввели неправильный пароль.' in element.text:
                raise LoginError(self.account_option, LoginErrorMessage.error_pass)
            raise LoginError(self.account_option, LoginErrorMessage.login_form_error)
        except TimeoutException:
            pass

    def should_be_login_button(self):
        try:
            self.search_element((By.CSS_SELECTOR, 'div.ctQZg.KtFt3 > div > div:nth-child(1)'), timeout=2,
                                type_wait=ec.presence_of_element_located)

        except TimeoutException:
            raise LoginError(self.account_option, LoginErrorMessage.not_login)

    def should_be_subscribe_and_unsubscribe_blocking(self):
        try:
            self.search_element((By.CSS_SELECTOR, 'div._08v79 > h3'), timeout=2,
                                type_wait=ec.presence_of_element_located)
            raise ActivBlocking(self.account_option, InformationMessage.subscribe_unsubscribe_blocking)

        except TimeoutException:
            pass

    def should_be_activity_blocking(self):
        try:
            error_message = self.search_element((By.CSS_SELECTOR, 'div > div.error-container > p'), timeout=2,
                                                type_wait=ec.presence_of_element_located)
            if 'Подождите несколько минут, прежде чем пытаться снова' in error_message.text:
                raise ActivBlocking(self.account_option, InformationMessage.activiti_blocking)
            else:
                print('Неизвестное всплывающее окно при вызове "should_be_activity_blocking".')
        except TimeoutException:
            pass

    def should_be_instagram_page(self):
        try:
            self.search_element((By.CSS_SELECTOR, '[href=\'/\']'), timeout=15,
                                type_wait=ec.presence_of_element_located)

        except TimeoutException:
            raise PageLoadingError(self.account_option, InformationMessage.page_loading_error)

    def standard_exception_handling(self):

        self.save_log_exception()
        exception_name = str(type(self.account_option.exception)).split("'")[1].split('.')[-1]
        if self.account_option.mode == self.account_option.parameters['fil'] \
                and isinstance(self.account_option.exception, KeyError):
            raise BotFinishTask(self.account_option, FilterMessage.list_empty)
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
