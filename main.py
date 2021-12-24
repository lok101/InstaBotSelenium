from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from module.support_funtion import SupportClass
from datetime import datetime
from data import username, password, proxy
from settings import *
import random
import time


class FunctionClass(SupportClass):
    # отписка от всех
    def unsubscribe_for_all_users(self,
                                  min_sleep=Unsubscribe.min_sleep,
                                  max_sleep=Unsubscribe.max_sleep,
                                  sleep_between_iterations=Unsubscribe.sleep_between_iterations,
                                  error_max=ErrorLimit.error_limit_unsubscribe
                                  ):
        """
        min_sleep - минимальная задежка между отписками
        max_sleep - максимальная задержка между отписками
        sleep_between_iterations - таймаут между итерациями (по 10 отписок за итерацию)
        error_max - колличество ошибок, которые пропуустит цикл. После превышения - остановка.
        """
        browser = self.browser
        browser.get(f"https://www.instagram.com/{username}/")
        # счётчик перезапусков
        error_count = 0

        while True:
            if error_count >= error_max:
                break
            try:
                following_count = browser.find_element(
                    By.XPATH, '//main/div/header/section/ul/li[3]/a/span').text
                print(f"Количество подписок: {following_count}")
                count = 10
                browser.get(f"https://www.instagram.com/{username}/")

                time.sleep(2)
                following_button = browser.find_element(By.XPATH, "//li[3]/a")
                following_button.click()
                time.sleep(2)

                # забираем все li из ul, в них хранится кнопка отписки и ссылки на подписки
                following_div_block = browser.find_element(By.XPATH, "/html/body/div[6]/div/div/div[3]/ul/div")
                following_users = following_div_block.find_elements(By.TAG_NAME, "li")
                time.sleep(2)

                for user in following_users:
                    if not count:
                        time.sleep(sleep_between_iterations)
                        break

                    user_url = user.find_element(By.TAG_NAME, "a").get_attribute("href")
                    user_name = user_url.split("/")[-2]

                    user.find_element(By.TAG_NAME, "button").click()
                    time.sleep(random.randrange(min_sleep, max_sleep))
                    browser.find_element(By.XPATH, "/html/body/div[7]/div/div/div/div[3]/button[1]").click()

                    print(f"Итерация #{count} >>> Отписался от пользователя {user_name}")
                    count -= 1
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
                time.sleep(30)
                continue

    # ставит лайки по хэштегу
    def like_photo_by_hashtag(self, hashtag,
                              min_sleep=Like.min_sleep,
                              max_sleep=Like.max_sleep
                              ):

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
    def subscribe_to_user_list(self,
                               user_list=Subscribe.user_list,
                               limit_subscribes=Subscribe.limit_subscribes,
                               timeout=Subscribe.timeout,
                               scatter_timeout=Subscribe.scatter_timeout,
                               subscribe_in_session=Subscribe.subscribe_in_session,
                               sleep_between_iterations=Subscribe.sleep_between_iterations
                               ):
        """
        user_list - список юзеров для подписки
        timeout - среднее время на одну подписку
        scatter_timeout - разброс при вычислении таймаута
        sleep_between_iterations - дополнительный таймаут на каждые subscribe_in_session подписок
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
{subscribe_in_session} пользователей. Таймаут {sleep_between_iterations} минут.')
                    time.sleep(sleep_between_iterations * 60)

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
                subscribe_count += 1
                print(f'Подпислся на пользователя: {user_name}, всего подписок: {subscribe_count - 1}')

            except NoSuchElementException:
                print('----------- Ошибка подписке, переход к следующему посту. -----------')
                input('============= Жми Enter =============')
                continue

            except AssertionError:
                time.sleep(2)
                continue


my_bot = FunctionClass(username, password, proxy=StartSettings.proxy, headless=StartSettings.headless)
try:
    my_bot.login()
    # my_bot.select_commentators()
    # my_bot.subscribe_to_user_list()
    my_bot.unsubscribe_for_all_users()
    # my_bot.select_commentators_many_posts()
finally:
    my_bot.close_browser()
