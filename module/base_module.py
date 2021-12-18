from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from data import username, password, tag
import time


class BaseClass:
    def __init__(self, user_name, pass_word, proxy=None, link='https://www.instagram.com/', timeout=10):
        if proxy is not None:
            self.browser = self.proxy_browser(proxy)
        else:
            self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(timeout)
        self.link = link
        self.username = user_name
        self.password = pass_word

    def login(self):
        browser = self.browser
        browser.get(self.link)
        time.sleep(3)

        username_input = browser.find_element(By.NAME, 'username')
        username_input.clear()
        username_input.send_keys(username)

        password_input = browser.find_element(By.NAME, 'password')
        password_input.clear()
        password_input.send_keys(password)

        password_input.send_keys(Keys.ENTER)
        time.sleep(6)

    def close_browser(self):
        self.browser.quit()

    def proxy_browser(self, proxy):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server=%s' % proxy)
        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.get('https://2ip.ru/')
        ip = self.browser.find_element(By.CSS_SELECTOR, 'div.ip span').text
        assert ip in proxy
        print(f'Подключение через прокси: {proxy}')
        return self.browser

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

    # возвращает список из девяти постов по хештегу
    def select_url_posts_to_hashtag(self, hashtag):
        browser = self.browser
        browser.get(f'https://www.instagram.com/explore/tags/{hashtag}/')
        posts_block = browser.find_element(By.XPATH, '//main/article/div[1]/div/div')
        posts = posts_block.find_elements_by_tag_name('a')
        posts_url_list = []

        for post in posts:
            post_url = post.get_attribute('href')
            if '/p/' in post_url:
                posts_url_list.append(post_url)
        print('Ссылки на посты собраны.')
        return posts_url_list

    # собирает список тех, кто комменировал посты, для сбора ссылок на посты вызывает "select_url_posts_to_hashtag"
    def select_commentators(self, hashtag=tag, number_scrolls=1, scrolls_timeout=1):
        """
        number_scrolls - колличество прокруток поля комметнариев у поста
        scrolls_timeout - задержка перед прокруткой (иначе может падать с ошибкой NoSuchElement)
        """
        browser = self.browser
        link_list = self.select_url_posts_to_hashtag(hashtag=hashtag)
        users_urls = set()
        for link in link_list:
            browser.get(link)
            comments_ul = browser.find_element(By.XPATH, '//div[2]/div/div[2]/div[1]/ul')

            for number in range(number_scrolls):
                browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", comments_ul)
                time.sleep(scrolls_timeout)

                plus_button = browser.find_element(By.XPATH, '//div/div[2]/div[1]/ul/li/div/button')
                plus_button.click()
                time.sleep(scrolls_timeout)

            comments_block = browser.find_element(By.XPATH, '//article/div/div[2]/div/div[2]/div[1]/ul')
            user_comment_block = comments_block.find_elements(By.TAG_NAME, 'a')

            for user_comment in user_comment_block:
                user_url = user_comment.get_attribute('href')
                len_user_url = len(user_url.split('/'))   # у ссылки на профиль пользователя это параметр равен пяти(5)
                if len_user_url == 5:
                    users_urls.add(user_url)
            print(f'Колличество собранных пользователей: {len(users_urls)}')
        return users_urls

    def test_method(self, link):
        browser = self.browser
        browser.get(link)
        assert self.should_be_limit_subscribes(5000)
        time.sleep(5)
