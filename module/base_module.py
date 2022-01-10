from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from data import proxy_list
from settings import *
import random
import requests
import time

username, password = '', ''


class BaseClass:
    def __init__(self, user_name, pass_word, headless_and_proxy,
                 proxy_url=(random.choice(proxy_list)),
                 link='https://www.instagram.com/',
                 ):
        """
        headless - запуск в режиме "без головы"
        timeout - таймаут implicitly_wait
        """
        global username, password
        username, password = user_name, pass_word

        chrome_options = webdriver.ChromeOptions()
        if headless_and_proxy[0].lower() == 'y':
            chrome_options.add_argument("--headless")
        if headless_and_proxy[1].lower() == 'y':
            self.browser = self.proxy_browser(proxy_url, chrome_options)
        else:
            self.browser = webdriver.Chrome(options=chrome_options)
        self.link = link
        self.username = user_name
        self.password = pass_word

    def login(self):
        browser = self.browser
        browser.get(self.link)
        print(f'Логин с аккаунта --- {username}')

        username_input = self.search_element((By.NAME, "username"))
        username_input.clear()
        username_input.send_keys(username)

        password_input = self.search_element((By.NAME, "password"))
        password_input.clear()
        password_input.send_keys(password)

        password_input.send_keys(Keys.ENTER)
        assert self.should_be_login_button(), 'Не получилось залогиниться'
        print('Залогинился.')

    def close_browser(self):
        self.browser.quit()

    def get_link(self, locator):
        item = self.search_element(locator)
        url = item.get_attribute('src')
        return url

    def proxy_browser(self, proxy_url, chrome_options):
        chrome_options.add_argument(f'--proxy-server=%s' % proxy_url)
        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.get('https://2ip.ru/')
        ip = self.search_element((By.CSS_SELECTOR, 'div.ip span'), type_wait=ec.presence_of_element_located).text
        assert ip in proxy_url
        print(f'Подключение через прокси: {proxy_url}')
        return self.browser

    @staticmethod
    def download_for_link(link):
        get_img = requests.get(link)
        with open('data/profile_avatar.jpg', 'wb') as img_file:
            img_file.write(get_img.content)

    @staticmethod
    def file_read(file_name, value, operating_mode='r'):
        with open(f'data/{file_name}.txt', operating_mode) as file:
            for link in file:
                value.add(link)

    @staticmethod
    def file_write(file_name, value, value2=None, operating_mode='a'):
        with open(f'data/{file_name}.txt', operating_mode) as file:
            if value2 is not None:
                file.write(str(value) + '\n')
                file.write(str(value2) + '\n \n')
            elif isinstance(value, list) or isinstance(value, set):
                for item in value:
                    file.write(item + '\n')
            else:
                file.write(str(value))

    # возвращает элемент с использованием явного ожидания
    def search_element(self, locator,
                       timeout=StartSettings.web_driver_wait,
                       type_wait=ec.element_to_be_clickable
                       ):
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
                        if len_user_url == 5 and 'www.instagram.com' in profile_url and username not in profile_url \
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
                        if len_user_url == 5 and 'www.instagram.com' in profile_url and username not in profile_url \
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

    # проверяет, если ли мини-иконка профиля (используется для проверки логина)
    def should_be_login_button(self):
        try:
            self.search_element((By.CSS_SELECTOR, 'div:nth-child(6) > span > img'),
                                type_wait=ec.presence_of_element_located)
            exist = True
        except TimeoutException:
            exist = False
        return exist

    # проверяет наличие "микробана" на подписку
    def should_be_subscribe_blocking(self):
        try:
            self.search_element((By.CSS_SELECTOR, 'div._08v79 > h3'), timeout=2,
                                type_wait=ec.presence_of_element_located)
            exist = False
        except TimeoutException:
            exist = True
        return exist

    # проверяет наличие "микробана" на активность
    def should_be_activity_blocking(self):
        exist = None
        try:
            error_message = self.search_element((By.CSS_SELECTOR, 'div > div.error-container > p'), timeout=2,
                                                type_wait=ec.presence_of_element_located)
            if 'Подождите несколько минут, прежде чем пытаться снова' in error_message.text:
                exist = False
        except TimeoutException:
            exist = True
        return exist
