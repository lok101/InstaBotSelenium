from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from data import username, password
from settings import *
import time


class BaseClass:
    def __init__(self, user_name, pass_word, proxy, headless,
                 link='https://www.instagram.com/',
                 implicitly_wait=StartSettings.implicitly_wait_timeout
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
            time.sleep(3)
        else:
            self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.implicitly_wait(implicitly_wait)
        self.link = link
        self.username = user_name
        self.password = pass_word

    def login(self):
        browser = self.browser
        browser.get(self.link)
        print(f'Логин с аккаунта --- {username}')
        time.sleep(3)

        username_input = browser.find_element(By.NAME, 'username')
        username_input.clear()
        username_input.send_keys(username)

        password_input = browser.find_element(By.NAME, 'password')
        password_input.clear()
        password_input.send_keys(password)

        password_input.send_keys(Keys.ENTER)
        time.sleep(6)
        assert self.should_be_login_button(), 'Не получилось залогиниться'
        print('Залогинился.')

    def close_browser(self):
        self.browser.quit()

    def proxy_browser(self, proxy, chrome_options):
        chrome_options.add_argument('--proxy-server=%s' % proxy)
        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.get('https://2ip.ru/')
        ip = self.browser.find_element(By.CSS_SELECTOR, 'div.ip span').text
        assert ip in proxy
        print(f'Подключение через прокси: {proxy}')
        return self.browser

    # проверяет, если ли кнопка логина, вернёт True, если кнопки НЕТ
    def should_be_login_button(self):
        browser = self.browser
        self.browser.implicitly_wait(1)
        try:
            browser.find_element(By.CSS_SELECTOR, 'span a button')
            exist = False
        except NoSuchElementException:
            exist = True
        return exist

    # проверяет, стоит ли лайк
    def should_be_like(self):
        browser = self.browser
        self.browser.implicitly_wait(1)
        try:
            browser.find_element(By.CSS_SELECTOR, 'span.fr66n > button > div.QBdPU.B58H7 > svg')
            exist = True
        except NoSuchElementException:
            exist = False
        return exist

    # проверяет, подписан ли на пользователя
    def should_be_subscribe(self):
        """
        вернёт False если если подписка уже есть
        """
        browser = self.browser
        self.browser.implicitly_wait(1)
        try:
            browser.find_element(By.XPATH, '//section/div[1]/div[1]/div/div[1]/button')
            exist = False
        except NoSuchElementException:
            exist = True
        return exist

    # проверяет, есть ли публикации в профиле
    def should_be_posts(self):
        """
        вернёт False если найдёт надпись "Публикаций пока нет"
        """
        browser = self.browser
        self.browser.implicitly_wait(1)
        try:
            browser.find_element(By.XPATH, '//article/div[1]/div/div[2]/h1')
            exist = False
        except NoSuchElementException:
            exist = True
        return exist

    # проверяет, являяется ли переданное число больше числа подписчиков на странице
    def should_be_limit_subscribes(self, limit_subscribes):
        browser = self.browser
        button_subscribes = browser.find_element(By.XPATH, '//header/section/ul/li[2]/a/span')
        number_subscribes_str = button_subscribes.get_attribute('title')
        number_subscribes_int = int(number_subscribes_str.replace(" ", ""))
        print(number_subscribes_int)
        if limit_subscribes > number_subscribes_int:
            return True
        return False

    # проверяет, не является ли профиль закрытым
    def should_be_privat_profile(self):
        """
        вернёт False если профиль закрыт
        """
        browser = self.browser
        self.browser.implicitly_wait(1)
        try:
            browser.find_element(By.XPATH, '//article/div[1]/div/h2')
            exist = False
        except NoSuchElementException:
            exist = True
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
        time.sleep(4)
        if parameter == 1:
            tags = self.browser.find_elements(By.TAG_NAME, 'a')
            for public_block in tags:
                profile_url = public_block.get_attribute('href')
                len_user_url = len(profile_url.split('/'))  # у ссылки на профиль пользователя это параметр равен пяти.
                if len_user_url == 5 and 'www.instagram.com' in profile_url and username not in profile_url\
                        and 'explore' not in profile_url and ignore not in profile_url:
                    list_urls.add(profile_url)

        elif parameter == 2:
            tags = self.browser.find_elements(By.TAG_NAME, 'a')
            for post in tags:
                post_url = post.get_attribute('href')
                if '/p/' in post_url:
                    list_urls.add(post_url)
        return list_urls
