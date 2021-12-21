from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from module.support_funtion import SupportClass
from datetime import datetime
from data import username, password, proxy
import random
import time


class FunctionClass(SupportClass):
    # отписка от всех
    def unsubscribe_for_all_users(self, min_sleep=4, max_sleep=9, sleep_between_iterations=50, error_max=5):
        browser = self.browser
        browser.get(f"https://www.instagram.com/{username}/")

        following_count = browser.find_element(
            By.XPATH, '//main/div/header/section/ul/li[3]/a/span').text
        print(f"Количество подписок: {following_count}")
        # счётчик перезапусков
        error_count = 0

        while True:
            browser.get(f"https://www.instagram.com/{username}/")
            if error_count >= error_max:
                break
            try:
                count = 10
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

    # подписыватеся в разных режимах
    def subscribe(self, operating_mode=1, limit_subscribes=5000,
                  timeout=5, scatter_timeout=3, subscribe_in_session=40, grand_timeout=50):
        """
        operating_mode1 - подписка на активных комментаторов по хэштегу
        operating_mode2 - подписка на подписчиков "по конкуренту"
        timeout - среднее время на одну подписку
        scatter_timeout - разброс при вычислении таймаута
        grand_timeout - дополнительный таймаут на каждые 50 подписок
        subscribe_in_session - колличество подписок в одной сессии, по истечению - ожидание grand_timeout
        limit_subscribes - максимальное число подписчиков у профиля (если больше, то пропустит этот профиль)
        """
        browser = self.browser
        subscribe_count = 1
        user_list, ignore_list = set(), set()
        path = ''

        if operating_mode == 1:
            print('Списка нет, вызываю "select_commentators"')
            self.select_commentators()
            path = 'data/User_urls_commentators.txt'
            print('Список получен, перехожу к подписке.')
        elif operating_mode == 2:
            print('Списка нет, вызываю "select_subscribes"')
            self.select_subscribes()
            path = 'data/User_urls_subscribers.txt'
            print('Список получен, перехожу к подписке.')

        with open(path, 'r') as file:
            for link in file:
                user_list.add(link)
        with open('data/ignore_list.txt', 'r') as file:
            for link in file:
                ignore_list.add(link)

        user_list = user_list.difference(ignore_list)

        for user in user_list:
            try:
                if subscribe_count % subscribe_in_session == 0:
                    print(f'{datetime.now().strftime("%H:%M")} Подписался на очередные \
    {subscribe_in_session} пользователей. Таймаут {grand_timeout} минут.')
                    time.sleep(grand_timeout * 60)

                browser.get(user)
                user_name = user.split("/")[-2]
                print(f'Перешёл в профиль: {user_name}')

                assert self.should_be_privat_profile(), 'Профиль закрыт, переход к следующему пользователю.'
                assert self.should_be_subscribe(), 'Уже подписан, переход к следующему пользователю.'
                assert self.should_be_posts(), '======= В профиле нет публикаций, переход к следующему пользователю.'
                assert self.should_be_limit_subscribes(limit_subscribes),\
                    f'Слишком много подписчиков. Усатновлен лимит: {limit_subscribes}'

                time.sleep(random.randrange(timeout - scatter_timeout, timeout + scatter_timeout))
                subscribe_button = browser.find_element(By.XPATH, '//div/div/div/span/span[1]/button')
                subscribe_button.click()
                ignore_list.add(user)
                subscribe_count += 1
                print(f'Подпислся на пользователя: {user_name}, всего подписок: {subscribe_count - 1}')

            except NoSuchElementException:
                print('----------- Ошибка подписке, переход к следующему посту. -----------')
                input('============= Жми Enter =============')
                continue

            except AssertionError:
                time.sleep(2)
                continue

            finally:
                with open('data/ignore_list.txt', 'w'):
                    for user_url in ignore_list:
                        file.write(user_url + '\n')
                print('Игнор лист дополнен.')


my_bot = FunctionClass(username, password)
try:
    my_bot.login()
    # my_bot.subscribe()
    my_bot.unsubscribe_for_all_users()
finally:
    my_bot.close_browser()
