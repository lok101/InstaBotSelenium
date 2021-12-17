from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from data import username, password, tag
from datetime import datetime
import random
import time


class InstagramBot:
    def __init__(self, user_name, pass_word, link='https://www.instagram.com/', timeout=10):
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
        number_subscribes = int(button_subscribes.get_attribute('title'))
        if limit_subscribes > number_subscribes:
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

    # отписка от всех
    def unsubscribe_for_all_users(self, min_sleep=4, max_sleep=9, sleep_between_iterations=20, error_max=5):
        browser = self.browser
        browser.get(f"https://www.instagram.com/{username}/")

        following_count = browser.find_element(
            By.XPATH, '//main/div/header/section/ul/li[3]/a/span').text
        print(f"Количество подписок: {following_count}")
        # счётчик перезапусков
        error_count = 0

        while True:
            if error_count >= error_max:
                break
            try:
                count = 10
                browser.get(f"https://www.instagram.com/{username}/")

                following_button = browser.find_element(By.XPATH, "//li[3]/a")
                following_button.click()

                # забираем все li из ul, в них хранится кнопка отписки и ссылки на подписки
                following_div_block = browser.find_element(By.XPATH, "/html/body/div[6]/div/div/div[3]/ul/div")
                following_users = following_div_block.find_elements(By.TAG_NAME, "li")

                for user in following_users:
                    if not count:
                        time.sleep(sleep_between_iterations)
                        break

                    user_url = user.find_element(By.TAG_NAME, "a").get_attribute("href")
                    user_name = user_url.split("/")[-2]

                    user.find_element(By.TAG_NAME, "button").click()
                    browser.find_element(By.XPATH, "/html/body/div[7]/div/div/div/div[3]/button[1]").click()

                    print(f"Итерация #{count} >>> Отписался от пользователя {user_name}")
                    count -= 1
                    time.sleep(random.randrange(min_sleep, max_sleep))
            except NoSuchElementException:
                error_count += 1
                if error_count == error_max:
                    print(f'''
                    -----------------------------------------------------------------------------------
                    ----------- Элемент не найден, лимит перезапусков превышен, завершение. -----------
                    -----------------------------------------------------------------------------------
                           ''')
                else:
                    print(f'''
                    -----------------------------------------------------------------------------------
                    ----------- Элемент не найден, перезапуск # {error_count}. ------------------------
                    -----------------------------------------------------------------------------------
                           ''')
                input('============= Жми Enter =============')
                time.sleep(3)
                continue

    # ставит лайки по хэштегу
    def like_photo_by_hashtag(self, hashtag, min_sleep=10, max_sleep=30):

        browser = self.browser
        browser.get(f'https://www.instagram.com/explore/tags/{hashtag}/')
        time.sleep(6)

        for i in range(1, 4):
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.randrange(2, 4))

        tags = browser.find_elements(By.TAG_NAME, 'a')
        posts_urls = [item.get_attribute('href') for item in tags if "/p/" in item.get_attribute('href')]
        print(f'Колличество постов для лайка >>> {len(posts_urls)}')

        for url in posts_urls:
            try:
                browser.get(url)
                assert self.should_be_like()
                button_like = browser.find_element(By.XPATH, '//section[1]/span[1]/button')
                button_like.click()
                print(f'Лайк на пост по ссылке: {url} --- поставлен!')
                time.sleep(random.randrange(min_sleep, max_sleep))
            except NoSuchElementException:
                print('----------- Ошибка при постановке лайка, переход к следующему посту. -----------')
                continue
            except AssertionError:
                print('----------- Лайк уже есть, переход к следующему посту. -----------')
                continue

    # подписыватеся на юзеров из списка, если нет списка, то вызывает "select_commentators"
    def subscribe_to_user_list(self, user_list=None, limit_subscribes=5000,
                               timeout=2, scatter_timeout=1, subscribe_in_session=50, grand_timeout=60):
        """
        user_list - список юзеров для подписки
        timeout - среднее время на одну подписку
        scatter_timeout - разброс при вычислении таймаута
        grand_timeout - дополнительный таймаут на каждые 50 подписок
        limit_subscribes - максимальное число подписчиков у профиля (если больше, то пропустит этот профиль)
        """
        browser = self.browser
        if user_list is None:
            print('Списка нет, вызываю "select_commentators"')
            user_list = self.select_commentators()
            print('Список получен, перехожу к подписке.')
        subscribe_count = 1

        for user in user_list:
            try:
                if subscribe_count % subscribe_in_session == 0:
                    print(f'{datetime.now().strftime("%H:%M")} Подписался на очередные \
{subscribe_in_session} пользователей. Таймаут {grand_timeout} минут.')
                    time.sleep(grand_timeout * 60)

                browser.get(user)
                user_name = user.split("/")[-2]
                print(f'Перешёл в профиль: {user_name}')

                assert self.should_be_privat_profile(), \
                    '----------- Профиль закрыт, переход к следующему пользователю. -----------'
                assert self.should_be_subscribe(), \
                    '----------- Уже подписан, переход к следующему пользователю. -----------'
                assert self.should_be_posts(), \
                    '----------- В профиле нет публикаций, переход к следующему пользователю. -----------'
                assert self.should_be_limit_subscribes(limit_subscribes), \
                    f'----------- Слишком много подписчиков. Усатновлен лимит: {limit_subscribes}-----------'

                time.sleep(random.randrange(timeout - scatter_timeout, timeout + scatter_timeout))
                subscribe_button = browser.find_element(By.XPATH, '//div/div/div/span/span[1]/button')
                subscribe_button.click()
                subscribe_count += 1
                print(f'Подпислся на пользователя: {user_name}, всего подписок: {subscribe_count - 1}')

            except NoSuchElementException:
                print('----------- Ошибка подписке, переход к следующему посту. -----------')
                input('============= Жми Enter =============')
                continue

            except AssertionError:
                time.sleep(2)
                continue


my_bot = InstagramBot(username, password)
try:
    my_bot.login()
    # my_bot.select_commentators()
    my_bot.subscribe_to_user_list()
    # my_bot.unsubscribe_for_all_users()
    # my_bot.select_commentators_many_posts()
finally:
    my_bot.close_browser()
