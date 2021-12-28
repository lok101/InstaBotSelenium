from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from data import username, password
from settings import *
import time


class BaseClass:
    def __init__(self, user_name, pass_word, proxy, headless,
                 link='https://www.instagram.com/',
                 ):
        """
        headless - запуск в режиме "без головы"
        timeout - таймаут implicitly_wait
        """
        chrome_options = webdriver.ChromeOptions()
        if headless == 'yes':
            chrome_options.add_argument("--headless")
        if proxy == 'yes':
            self.browser = self.proxy_browser(proxy, chrome_options)
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

    def proxy_browser(self, proxy, chrome_options):
        chrome_options.add_argument('--proxy-server=%s' % proxy)
        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.get('https://2ip.ru/')
        ip = self.search_element((By.CSS_SELECTOR, 'div.ip span'), type_wait=ec.presence_of_element_located).text
        assert ip in proxy
        print(f'Подключение через прокси: {proxy}')
        return self.browser

    # возвращает элемент с использованием явного ожидания
    def search_element(self, locator,
                       timeout=StartSettings.web_driver_wait,
                       type_wait=StartSettings.web_driver_wait_type
                       ):
        element = WebDriverWait(self.browser, timeout).until(type_wait(locator))
        return element

    # проверяет, если ли кнопка логина, вернёт True, если кнопки НЕТ
    def should_be_login_button(self):
        try:
            self.search_element((By.CSS_SELECTOR, 'span a button'))
            exist = False
        except TimeoutException:
            exist = True
        return exist

    # проверяет, стоит ли лайк
    def should_be_like(self):
        try:
            self.search_element((By.CSS_SELECTOR, 'span.fr66n > button > div.QBdPU.B58H7 > svg'), timeout=1)
            exist = True
        except TimeoutException:
            exist = False
        return exist

    # проверяет, подписан ли на пользователя
    def should_be_subscribe(self):
        """
        вернёт False если если подписка уже есть
        """
        try:
            self.search_element((By.XPATH, '//section/div[1]/div[1]/div/div[1]/button'), timeout=1)
            exist = False
        except TimeoutException:
            exist = True
        return exist

    # проверяет, есть ли публикации в профиле
    def should_be_posts(self):
        """
        вернёт False если найдёт надпись "Публикаций пока нет"
        """
        try:
            self.search_element((By.XPATH, '//article/div[1]/div/div[2]/h1'), timeout=1)
            exist = False
        except TimeoutException:
            exist = True
        return exist

    # проверяет, являяется ли переданное число больше числа подписчиков на странице
    def should_be_limit_subscribes(self, limit_subscribes):
        try:
            button_subscribes = self.search_element((By.XPATH, '//header/section/ul/li[2]/a/span'),
                                                    type_wait=ec.presence_of_element_located)
            assert button_subscribes
            number_subscribes_str = button_subscribes.get_attribute('title')
            number_subscribes_int = int(number_subscribes_str.replace(" ", ""))
            if limit_subscribes > number_subscribes_int:
                return True
            return False
        except AssertionError:
            return False

    # проверяет, не является ли профиль закрытым
    def should_be_privat_profile(self):
        """
        вернёт False если профиль закрыт
        """
        try:
            self.search_element((By.XPATH, '//article/div[1]/div/h2'), timeout=1)
            exist = False
        except TimeoutException:
            exist = True
        except StaleElementReferenceException:
            print('Проблемы при поиске элемента, пропускаю профиль')
            exist = False
        return exist

    # возвращает список по тегу
    def tag_search(self, parameter=1, ignore=None):
        """
        parameter=1 - возвращает список ссылок на профили
        parameter=2 - возвращает список ссылок на посты
        ignore - ключевое слово для игнора (сверяется со ссылкой)
        """
        print(f'Вызван tag_search с параметром: {parameter}')
        list_urls = set()
        time.sleep(5)
        if parameter == 1:
            tags = self.browser.find_elements(By.TAG_NAME, 'a')
            for public_block in tags:
                profile_url = public_block.get_attribute('href')
                len_user_url = len(profile_url.split('/'))  # у ссылки на профиль пользователя это параметр равен пяти.
                if len_user_url == 5 and 'www.instagram.com' in profile_url and username not in profile_url\
                        and 'explore' not in profile_url and ignore not in profile_url:
                    list_urls.add(profile_url)

        elif parameter == 2:
            tags = self.search_element((By.TAG_NAME, 'a'))
            for post in tags:
                post_url = post.get_attribute('href')
                if '/p/' in post_url:
                    list_urls.add(post_url)
        return list_urls
