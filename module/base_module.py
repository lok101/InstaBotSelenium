from datetime import datetime
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from data import proxy_list
from settings import *
import requests
import traceback
import pickle
import time
import re
import json


class LoginError(Exception):
    pass


class ActivBlocking(Exception):
    pass


class BaseClass:
    def __init__(self, user_name, pass_word, headless_and_proxy,
                 link='https://www.instagram.com/',
                 ):
        """
        headless - запуск в режиме "без головы"
        timeout - таймаут implicitly_wait
        """

        chrome_options = webdriver.ChromeOptions()
        if headless_and_proxy[0].lower() == 'y':
            chrome_options.add_argument("--headless")
        if headless_and_proxy[1].lower() == 'y':
            self.browser = self.proxy_browser(chrome_options)
        else:
            self.browser = webdriver.Chrome(options=chrome_options)
        self.link = link
        self.username = user_name
        self.password = pass_word

        self.subscribe = None
        self.mode = None   # присваивается внутри задачи, используется для вызова методов логирования и печати

    def login(self):
        try:
            browser = self.browser
            browser.get(self.link)
            assert self.should_be_home_page(), 'Не загрузил домашнюю страницу.'
            print(f'Логин с аккаунта - {self.username}')
            browser.delete_all_cookies()
            for cookie in pickle.load(open(f'data/cookies/{self.username}_cookies', 'rb')):
                browser.add_cookie(cookie)
            time.sleep(1)
            browser.refresh()
            assert self.should_be_login_button(), 'Не получилось залогиниться.'
            print('Залогинился через cookies.')

        except AssertionError as assertion:
            assertion = str(assertion.args)
            text = re.sub("[)(',]", '', assertion)
            date = datetime.now().strftime("%d-%m %H:%M:%S")
            log = f'{date}  <вход через cookies> -- {self.username}: {text}\n'
            self.file_write('logs/authorize_error', log)
            raise LoginError(f'{text}')

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
                assert self.should_be_login_form_error(), 'Ошибка авторизации. Красный текст под формой).'
                assert self.should_be_verification_email(), 'Подозрительная попытка входа.'
                assert self.should_be_phone_number_input(), 'Требуется ввод номера телефона.'
                assert self.should_be_verification_phone_number(), 'Требуется код из СМС.'
                assert self.should_be_login_button(), 'Не получилось залогиниться.'

                # сохраняем cookies
                pickle.dump(browser.get_cookies(), open(f'data/cookies/{self.username}_cookies', 'wb'))

            except AssertionError as assertion:
                assertion = str(assertion.args)
                text = re.sub("[)(',]", '', assertion)
                date = datetime.now().strftime("%d-%m %H:%M:%S")
                log = f'{date} -- {self.username}: {text}\n'
                self.file_write('logs/authorize_error', log)
                raise LoginError(f'= = = = = = = = = = {text} = = = = = = = = = =')

            print(f'Залогинился и создал cookies ===> data/cookies/{self.username}_cookies.')

    def close_browser(self):
        self.browser.quit()

    def get_link(self, locator):
        item = self.search_element(locator)
        url = item.get_attribute('src')
        return url

    def proxy_browser(self, chrome_options, proxy=proxy_list):
        chrome_options.add_argument('--proxy-server=%s' % proxy)
        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.get("https://api.myip.com/")
        # noinspection PyTypeChecker
        pre = self.search_element((By.TAG_NAME, "body"), type_wait=ec.presence_of_element_located).text
        ip = json.loads(pre)['ip']
        assert ip not in '78.139.68.238'
        print(f'Подключение через прокси: {ip}')
        return self.browser

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
    def print_and_save_log_traceback(self, type_traceback, end_str='\n'):
        traceback_text = traceback.format_exc().split('Stacktrace:')[0]
        date = datetime.now().strftime("%d-%m %H:%M:%S")
        path = f'logs/{self.mode}/{type_traceback}'
        self.file_write(path, date, traceback_text)
        print(f'>> {type_traceback}. Запись добавлена в лог: {path}', end=end_str)

    # возвращает элемент с использованием явного ожидания
    def search_element(self, locator, timeout=StartSettings.web_driver_wait, type_wait=ec.element_to_be_clickable):
        element = WebDriverWait(self.browser, timeout).until(type_wait(locator))
        return element

    # возвращает список по тегу
    def tag_search(self, parameter=1, ignore=None):
        """
        parameter=1 - возвращает список ссылок на профили
        parameter == 1.5 - возвращает список ссылок на профили в выпадающем меню поиска
        parameter=2 - возвращает список ссылок на посты
        ignore - ключевое слово для игнора (сверяется со ссылкой)
        """
        # print(f'Вызван tag_search с параметром: {parameter}')
        list_urls = set()
        while True:
            try:
                if parameter == 1:
                    self.search_element((By.CSS_SELECTOR, 'div.Pkbci > button'))
                    tags = self.browser.find_elements(By.TAG_NAME, 'a')
                    for public_block in tags:
                        profile_url = public_block.get_attribute('href')
                        len_user_url = len(profile_url.split('/'))  # у ссылки на профиль равен пяти.
                        if len_user_url == 5 and 'www.instagram.com' in profile_url and self.username not in profile_url \
                                and 'explore' not in profile_url and ignore not in profile_url:
                            list_urls.add(profile_url)
                    return list_urls

                elif parameter == 1.5:
                    list_urls = []
                    self.search_element((By.CSS_SELECTOR, 'div > a.-qQT3'))
                    tags = self.browser.find_elements(By.TAG_NAME, 'a')
                    for public_block in tags:
                        profile_url = public_block.get_attribute('href')
                        len_user_url = len(profile_url.split('/'))  # у ссылки на профиль равен пяти.
                        if len_user_url == 5 and 'www.instagram.com' in profile_url and self.username not in profile_url \
                                and 'explore' not in profile_url and ignore not in profile_url:
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
            self.search_element((By.CSS_SELECTOR, 'div:nth-child(6) > span > img'),
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

    # проверяет, существует ли данная страница
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

    # проверяет наличие окна ошибки подключения - НЕ СРАБАТЫВАЕТ
    def should_be_error_connection_page(self):
        try:
            # noinspection PyTypeChecker
            self.search_element((By.ID, '#t'), timeout=1,
                                type_wait=ec.presence_of_element_located)
            exist = False
        except TimeoutException:
            exist = True
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
            return button
        else:
            return None

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

    def go_to_user_page(self, url, account='Не присвоен.'):
        self.browser.get(url)
        username = url.split("/")[-2]
        print(f'{datetime.now().strftime("%H:%M:%S")} - {account} - Перешёл в профиль: {username}', end=' ======> ')

        assert self.should_be_user_page(), 'Страница не существует'
        assert self.should_be_error_connection_page(), 'Ошибка загрузки страницы.'
        assert self.should_be_activity_blocking(), 'Микробан активности.'

    def go_to_my_profile_page(self):
        url = f'https://www.instagram.com/{self.username}/'
        self.browser.get(url)
        assert self.should_be_error_connection_page(), 'Ошибка загрузки страницы.'
        assert self.should_be_activity_blocking(), 'Микробан активности.'
