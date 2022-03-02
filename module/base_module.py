import data
from module.message_text_module import ErrorMessage, LoginErrorMessage, FilterMessage
from datetime import datetime
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from module.exception_module import LoginError, ActivBlocking, VerificationError
from selenium import webdriver
from data import proxy_list
from settings import *
import requests
import traceback
import random
import pickle
import time
import json


class BaseClass:

    def __init__(self):

        self.link = 'https://www.instagram.com/'
        self.username = None
        self.password = None
        self.browser = None
        self.headless = True
        self.proxy = True
        self.working_mode = None
        self.chrome_options = None
        self.file_name = None

        self.cycle = None
        self.max_timeout = None
        self.min_timeout = None
        self.mode = 'authorize'
        self.count_iteration = None
        self.count_limit = None
        self.subscribe = None
        self.timeout = None
        self.stop_word = None
        self.user_url = None
        self.exception_text = None

    def browser_parameter(self):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--log-level=3')
        if self.headless is True:
            self.chrome_options.add_argument("--headless")
        if self.proxy is True:
            self.chrome_options.add_argument(f'--proxy-server={proxy_list}')

    def parameter_input(self):
        self.working_mode = input('Укажите режим работы (-параметры): ')
        if '-p' in self.working_mode:
            self.proxy = False
        if '-h' in self.working_mode:
            self.headless = False

    def login(self):
        while True:
            try:
                try:
                    self.browser = webdriver.Chrome(options=self.chrome_options)
                    if self.proxy is True:
                        self.browser.get("https://api.myip.com/")
                        # noinspection PyTypeChecker
                        pre = self.search_element((By.TAG_NAME, "body"), type_wait=ec.presence_of_element_located).text
                        ip = json.loads(pre)['ip']
                        assert ip not in data.my_ip
                        print(f'Подключение через прокси: {ip}')

                    self.browser.get(self.link)
                    assert self.should_be_home_page(), LoginErrorMessage.not_login_page
                    print(f'Логин с аккаунта - {self.username}', end=' ===> ')
                    self.browser.delete_all_cookies()
                    for cookie in pickle.load(open(f'data/cookies/{self.username}_cookies', 'rb')):
                        self.browser.add_cookie(cookie)
                    time.sleep(1)
                    self.browser.refresh()
                    assert self.should_be_verification_form(), LoginErrorMessage.verification_form
                    assert self.should_be_login_button(), LoginErrorMessage.not_login_cookies
                    print('Залогинился через cookies.')

                except AssertionError as assertion:
                    self.exception_text = str(assertion.args)[2:-3]
                    date = datetime.now().strftime("%d-%m %H:%M:%S")
                    log = f'{date}  <вход через cookies> -- {self.username}: {self.exception_text}\n'
                    self.file_write('logs/authorize/authorize_error', log)
                    raise LoginError(f'{self.exception_text}')

                except FileNotFoundError:
                    try:
                        browser = self.browser
                        browser.get(self.link)
                        print(f'Логин с аккаунта --- {self.username}')

                        username_input = self.search_element((By.NAME, "username"))
                        username_input.clear()
                        username_input.send_keys(self.username)

                        password_input = self.search_element((By.NAME, "password"))
                        password_input.clear()
                        password_input.send_keys(self.password)

                        password_input.send_keys(Keys.ENTER)
                        time.sleep(5)
                        assert self.should_be_login_form_error(), LoginErrorMessage.login_form_error
                        assert self.should_be_verification_form(), LoginErrorMessage.verification_form
                        assert self.should_be_verification_email(), LoginErrorMessage.verification_email
                        assert self.should_be_phone_number_input(), LoginErrorMessage.input_phone_number
                        assert self.should_be_verification_phone_number(), LoginErrorMessage.input_code_from_sms
                        assert self.should_be_login_button(), LoginErrorMessage.not_login

                        # сохраняем cookies
                        pickle.dump(browser.get_cookies(), open(f'data/cookies/{self.username}_cookies', 'wb'))

                    except AssertionError as assertion:
                        text = str(assertion.args)[2:-3]
                        date = datetime.now().strftime("%d-%m %H:%M:%S")
                        log = f'{date} -- {self.username}: {text}\n'
                        self.file_write('logs/authorize/authorize_error', log)
                        print(f'= = = = {text} = = = =')
                        raise LoginError(f'{text}')

                    except Exception as ex:
                        self.exception_text = str(type(ex)).split("'")[1].split('.')[-1]
                        self.print_and_save_log_traceback()

                    print(f'Залогинился и создал cookies ===> data/cookies/{self.username}_cookies.')

                except Exception as ex:
                    self.exception_text = str(type(ex)).split("'")[1].split('.')[-1]
                    self.print_and_save_log_traceback()

            except ConnectionError:
                continue
            else:
                break

    def close_browser(self):
        self.browser.quit()

    def get_link(self, locator):
        # noinspection PyTypeChecker
        item = self.search_element(locator, type_wait=ec.presence_of_element_located, timeout=10)
        url = item.get_attribute('src')
        return url

    @staticmethod
    def download_for_link(link):
        get_img = requests.get(link)
        with open('data/profile_avatar.jpg', 'wb') as img_file:
            img_file.write(get_img.content)

    @staticmethod
    def file_read(file_name, value, operating_mode='r'):
        with open(f'data/{file_name}.txt', operating_mode) as file:
            if isinstance(value, set):
                for link in file:
                    value.add(link)
            elif isinstance(value, list):
                for link in file:
                    value.append(link)

    @staticmethod
    def file_write(file_name, value, value2=None, operating_mode='a'):
        with open(f'data/{file_name}.txt', operating_mode) as file:
            if value2 is not None:
                file.write(str(value) + '\n')
                file.write(str(value2) + '\n \n')
            elif isinstance(value, (list, set)):
                if '\n' in value.pop():
                    for item in value:
                        file.write(item)
                else:
                    for item in value:
                        file.write(item + '\n')
            else:
                file.write(str(value))

    # сохраняет лог исключения в файл и печатает сообщение об исключении в консоль
    def print_and_save_log_traceback(self, end_str='\n'):
        traceback_text = traceback.format_exc().split('Stacktrace:')[0]
        date = datetime.now().strftime("%d-%m %H:%M:%S")
        path = f'logs/{self.mode}/{self.exception_text}'
        self.file_write(path, date, traceback_text)
        if 'CONNECTION_FAILED' in traceback_text:
            timeout = StartSettings.err_proxy_timeout
            error_name = traceback_text.split('net::')[1].split('\n')[0]
            print(f'>> {error_name}. Запись добавлена в лог. Таймаут {timeout} секунд.', end=end_str)
            time.sleep(timeout)
        else:
            print(f'>> {self.mode} >> {self.exception_text}. Запись добавлена в лог.', end=end_str)

    def print_log_assert_and_control_cycle(self):
        if ErrorMessage.subscribe_blocking in self.exception_text:
            print('= = = = МИКРОБАН ПОДПИСКИ = = = =')
            raise ActivBlocking

        if ErrorMessage.unsubscribe_blocking in self.exception_text:
            print('= = = = МИКРОБАН ОТПИСКИ = = = =')
            raise ActivBlocking

        if ErrorMessage.activiti_blocking in self.exception_text:
            print('= = = = МИКРОБАН АКТИВНОСТИ = = = =')
            raise ActivBlocking

        if LoginErrorMessage.verification_form in self.exception_text:
            date = datetime.now().strftime("%d-%m %H:%M:%S")
            log = f'{date}  {self.mode} -- {self.username}: {self.exception_text}\n'
            self.file_write('logs/authorize/authorize_error', log)
            print('Получен запрос на верификацию.')
            raise VerificationError

        if ErrorMessage.page_not_found in self.exception_text:
            if self.mode == 'selection':
                print('Страница больше недоступна по этому адресу. Добавлена запись в лог.')
                date = datetime.now().strftime("%d-%m %H:%M:%S")
                log = f'{date} -- {self.user_url}\n'
                self.file_write('logs/selection/invalid_url', log)
            else:
                print('Страница больше недоступна.')
                self.file_write('ignore_list', self.user_url)

        elif ErrorMessage.page_loading_error in self.exception_text:
            sleep = StartSettings.sleep_page_not_found
            print(f'<< Страница не загрузилась. Жду {sleep} секунд. >>')
            time.sleep(sleep)

        elif FilterMessage.stop_word in self.exception_text:
            assert_log = f'{str(self.stop_word)} ===> {self.user_url}'
            self.file_write('logs/assert_stop_word_log', assert_log)
            self.file_write('ignore_list', self.user_url)
            print(f'{FilterMessage.stop_word}')
            time.sleep(self.timeout)

        elif FilterMessage.bad_profile in self.exception_text:
            assert_log = f'{self.user_url}'
            self.file_write('logs/assert_bad_profile_log', assert_log)
            self.file_write('ignore_list', self.user_url)
            print(f'{FilterMessage.bad_profile}')
            time.sleep(self.timeout)

        else:
            if self.mode == 'filtered':
                self.file_write('ignore_list', self.user_url)
                print(f'{self.exception_text[2:-3]}')
            else:
                print(f'Assert не был обработан -- {self.exception_text[2:-3]}')

    # возвращает элемент с использованием явного ожидания
    def search_element(self, locator, timeout=StartSettings.web_driver_wait, type_wait=ec.element_to_be_clickable):
        element = WebDriverWait(self.browser, timeout).until(type_wait(locator))
        return element

    # возвращает список по тегу
    def tag_search(self, parameter=1, ignore=None):
        """
        Parameter = 1 - возвращает список ссылок на профили
        parameter == 1.5 - возвращает список ссылок на профили в выпадающем меню поиска
        ignore - ключевое слово для игнорирования (сверяется со ссылкой)
        """
        list_urls = set()
        while True:
            try:
                if parameter == 1:
                    self.search_element((By.CSS_SELECTOR, 'div.Pkbci > button'))
                    tags = self.browser.find_elements(By.TAG_NAME, 'a')
                    for public_block in tags:
                        profile_url = public_block.get_attribute('href')
                        len_user_url = len(profile_url.split('/'))  # у ссылки на профиль равен пяти.
                        if len_user_url == 5 \
                                and 'www.instagram.com' in profile_url \
                                and self.username not in profile_url \
                                and 'explore' not in profile_url \
                                and ignore not in profile_url:
                            list_urls.add(profile_url)
                    return list_urls

                elif parameter == 1.5:
                    list_urls = []
                    self.search_element((By.CSS_SELECTOR, 'div > a.-qQT3'))
                    tags = self.browser.find_elements(By.TAG_NAME, 'a')
                    for public_block in tags:
                        profile_url = public_block.get_attribute('href')
                        len_user_url = len(profile_url.split('/'))  # у ссылки на профиль равен пяти.
                        if len_user_url == 5 \
                                and 'www.instagram.com' in profile_url \
                                and self.username not in profile_url \
                                and 'explore' not in profile_url \
                                and ignore not in profile_url:
                            list_urls.append(profile_url)
                    return list_urls

                elif parameter == 2:
                    time.sleep(5)
                    tags = self.browser.find_elements(By.TAG_NAME, 'a')
                    for post in tags:
                        post_url = post.get_attribute('href')
                        if '/p/' in post_url:
                            list_urls.add(post_url)
                    return list_urls

            except StaleElementReferenceException:
                print(StaleElementReferenceException)
                continue

    # возвращает список из 9 постов по хештегу
    def select_url_posts_to_hashtag(self, hashtag):
        browser = self.browser
        browser.get(f'https://www.instagram.com/explore/tags/{hashtag}/')
        posts_block = self.search_element((By.XPATH, '//main/article/div[1]/div/div'))
        posts = posts_block.find_elements_by_tag_name('a')
        posts_url_list = []

        for post in posts:
            post_url = post.get_attribute('href')
            if '/p/' in post_url:
                posts_url_list.append(post_url)
        print('Ссылки на посты собраны.')
        return posts_url_list

    # проверяет, если ли мини-иконка профиля (используется для проверки входа в аккаунт)
    def should_be_login_button(self):
        try:
            # noinspection PyTypeChecker
            self.search_element((By.CSS_SELECTOR, 'div:nth-child(6) > span > img'), timeout=2,
                                type_wait=ec.presence_of_element_located)
            exist = True
        except TimeoutException:
            exist = False
        return exist

    # проверяет наличие "микробана" на подписку/отписку
    def should_be_subscribe_and_unsubscribe_blocking(self):
        try:
            # noinspection PyTypeChecker
            self.search_element((By.CSS_SELECTOR, 'div._08v79 > h3'), timeout=2,
                                type_wait=ec.presence_of_element_located)
            exist = False
        except TimeoutException:
            exist = True
        return exist

    # проверяет наличие "микробана" на активность
    def should_be_activity_blocking(self):
        try:
            # noinspection PyTypeChecker
            error_message = self.search_element((By.CSS_SELECTOR, 'div > div.error-container > p'), timeout=2,
                                                type_wait=ec.presence_of_element_located)
            if 'Подождите несколько минут, прежде чем пытаться снова' in error_message.text:
                exist = False
            else:
                exist = True
        except TimeoutException:
            exist = True
        return exist

    # проверяет, существует ли страница по данной ссылке
    def should_be_user_page(self):
        while True:
            try:
                # noinspection PyTypeChecker
                error_message = self.search_element((By.CSS_SELECTOR, 'div > div > h2'), timeout=1,
                                                    type_wait=ec.presence_of_element_located)
                if 'К сожалению, эта страница недоступна' in error_message.text:
                    exist = False
                else:
                    exist = True
                break

            except TimeoutException:
                exist = True
                break

            except StaleElementReferenceException:
                continue
        return exist

    # проверяет, находится ли на странице инстаграм (ищет иконку справа-сверху)
    def should_be_instagram_page(self):
        try:
            # noinspection PyTypeChecker
            self.search_element((By.CSS_SELECTOR, '[href=\'/\']'), timeout=15,
                                type_wait=ec.presence_of_element_located)
            exist = True
        except TimeoutException:
            exist = False
        return exist

    # проверяет наличие окна "добавьте номер телефона"
    def should_be_phone_number_input(self):
        try:
            # noinspection PyTypeChecker
            self.search_element((By.CSS_SELECTOR, 'div.qF0y9.Igw0E.IwRSH.eGOV_._4EzTm.dQ9Hi > h3'), timeout=1,
                                type_wait=ec.presence_of_element_located)
            exist = False
        except TimeoutException:
            exist = True
        return exist

    # проверяет наличие окна "подтвердите номер телефона"
    def should_be_verification_phone_number(self):
        try:
            # noinspection PyTypeChecker
            self.search_element((By.XPATH, '/html/body/div[1]/section/main/div[2]/div/div/div/div[1]/div[1]/span'),
                                timeout=1, type_wait=ec.presence_of_element_located)
            exist = False
        except TimeoutException:
            exist = True
        return exist

    # проверяет наличие запроса на верификацию
    def should_be_verification_form(self):
        try:
            # noinspection PyTypeChecker
            self.search_element((By.CSS_SELECTOR, 'div.ctQZg.KtFt3 > button > div'), timeout=2)
            exist = False
        except TimeoutException:
            exist = True
        return exist

    # проверяет наличие окна "подтвердите почту"
    def should_be_verification_email(self):
        try:
            # noinspection PyTypeChecker
            self.search_element((By.CSS_SELECTOR, 'div > div.GNbi9 > div > p'),
                                timeout=1, type_wait=ec.presence_of_element_located)
            exist = False
        except TimeoutException:
            exist = True
        return exist

    # проверяет наличие ошибки "Не получилось залогиниться" (красный шрифт под формой авторизации).
    def should_be_login_form_error(self):
        try:
            # noinspection PyTypeChecker
            self.search_element((By.CSS_SELECTOR, '#slfErrorAlert'),
                                timeout=1, type_wait=ec.presence_of_element_located)
            exist = False
        except TimeoutException:
            exist = True
        return exist

    # ищет и нажимает кнопку "подписаться"
    def press_to_button_subscribe(self):
        button = self.search_element((By.XPATH, '//button'))
        if 'подписаться' in button.text.lower():
            iteration_limit = 10
            iteration_count = 0
            while iteration_count < iteration_limit:
                iteration_count += 1
                button.click()
                time.sleep(random.randrange(self.min_timeout, self.max_timeout))
                assert self.should_be_subscribe_and_unsubscribe_blocking(), ErrorMessage.subscribe_blocking
                self.file_write('ignore_list', self.user_url)
                self.count_iteration += 1
                print('Успешно.')
                break
        else:
            print('Кнопка не найдена.')
            self.file_write('ignore_list', self.user_url)
            time.sleep(random.randrange(Subscribe.min_timeout, Subscribe.max_timeout))

    # проверяет, находится ли на странице логина
    def should_be_home_page(self):
        try:
            # noinspection PyTypeChecker
            self.search_element((By.NAME, "username"),
                                timeout=10, type_wait=ec.presence_of_element_located)
            exist = True
        except TimeoutException:
            exist = False
        return exist

    # возвращает количество постов, подписчиков, подписок и коэффициент подписки/подписчики
    def return_number_posts_subscribe_and_subscribers(self):
        dict_return = dict()
        try:
            # noinspection PyTypeChecker
            subscriptions_field = self.search_element((By.CSS_SELECTOR, 'li:nth-child(3) > a > div > span.g47SY'),
                                                      type_wait=ec.presence_of_element_located, timeout=3)

            dict_return['subs'] = int(
                subscriptions_field.text.replace(" ", "").replace(',', ''))
        except TimeoutException:
            dict_return['subs'] = 0

        try:
            # noinspection PyTypeChecker
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

        # noinspection PyTypeChecker
        post_number_field = self.search_element((By.CSS_SELECTOR, 'li:nth-child(1) > div > span.g47SY'),
                                                type_wait=ec.presence_of_element_located)
        dict_return['posts'] = int(
            post_number_field.text.replace(" ", "").replace(',', '').replace('тыс.', '000').replace('млн', '000000'))

        return dict_return

    # переходит на страницу по ссылке, запускает проверки на наличие страницы, загрузку страницы и наличие микробана
    def go_to_user_page(self, end_str=' ===> '):
        self.browser.get(self.user_url)
        username = self.user_url.split("/")[-2]
        print(
          f'{datetime.now().strftime("%H:%M:%S")} - {self.username} - [{self.count_iteration + 1}/{self.count_limit}]',
          f'Перешёл в профиль: {username}', end=end_str)

        assert self.should_be_instagram_page(), ErrorMessage.page_loading_error
        assert self.should_be_activity_blocking(), ErrorMessage.activiti_blocking
        assert self.should_be_user_page(), ErrorMessage.page_not_found
        assert self.should_be_verification_form(), LoginErrorMessage.verification_form

    # переходит на свою страницу, запускает проверки на загрузку страницы и наличие микробана
    # возвращает количество подписок
    def go_to_my_profile_page(self, end_str='\n'):
        url = f'https://www.instagram.com/{self.username}/'
        self.browser.get(url)
        assert self.should_be_instagram_page(), ErrorMessage.page_loading_error
        assert self.should_be_activity_blocking(), ErrorMessage.activiti_blocking
        assert self.should_be_verification_form(), LoginErrorMessage.verification_form
        self.subscribe = self.return_number_posts_subscribe_and_subscribers()['subs']
        print(f"Количество подписок: {self.subscribe}", end=end_str)

    def difference_sets(self, item1, item2, item3=None):
        user_set1, user_set2, user_set3 = set(), set(), set()
        if item3 is not None:
            if isinstance(item1, str):
                self.file_read(item1, user_set1)
                self.file_read(item2, user_set2)
                self.file_read(item3, user_set3)
                final_set = user_set1.difference(user_set2, user_set3)
            elif isinstance(item1, set):
                self.file_read(item2, user_set2)
                self.file_read(item3, user_set3)
                final_set = item1.difference(user_set2, user_set3)
        else:
            if isinstance(item1, str):
                self.file_read(item1, user_set1)
                self.file_read(item2, user_set2)
                final_set = user_set1.difference(user_set2)
            elif isinstance(item1, set):
                self.file_read(item2, user_set2)
                final_set = item1.difference(user_set2)
        return final_set
