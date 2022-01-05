from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from module.support_funtion import SupportClass
from datetime import datetime
from data import *
from settings import *
import random
import time
import re


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
                following_count = self.search_element((
                    By.XPATH, '//main/div/header/section/ul/li[3]/a/span'),
                    type_wait=ec.presence_of_element_located).text
                print(f"Количество подписок: {following_count}")
                count = 10
                browser.get(f"https://www.instagram.com/{username}/")

                following_button = self.search_element((By.XPATH, "//li[3]/a"))
                following_button.click()

                # забираем все li из ul, в них хранится кнопка отписки и ссылки на подписки
                following_div_block = self.search_element((By.XPATH, "/html/body/div[6]/div/div/div[3]/ul/div"))
                time.sleep(2)
                following_users = following_div_block.find_elements(By.TAG_NAME, "li")

                for user in following_users:
                    if not count:
                        time.sleep(sleep_between_iterations)
                        break

                    # user_url = self.browser.find_element(By.TAG_NAME, "a").get_attribute("href")
                    # user_name = user_url.split("/")[-2]

                    unsubscribe_button = user.find_element(By.TAG_NAME, "button")
                    # unsubscribe_button = user.search_element((By.TAG_NAME, "button"))
                    unsubscribe_button.click()
                    time.sleep(random.randrange(min_sleep, max_sleep))
                    self.search_element((By.CSS_SELECTOR, "button.-Cab_")).click()

                    print(f"Итерация #{count} >>> Отписался от пользователя  {datetime.now().strftime('%H:%M:%S')}")
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

        tags = self.search_element((By.TAG_NAME, 'a'))
        posts_urls = [item.get_attribute('href') for item in tags if "/p/" in item.get_attribute('href')]
        print(f'Колличество постов для лайка >>> {len(posts_urls)}')

        for url in posts_urls:
            try:
                browser.get(url)
                assert self.should_be_like()
                button_like = self.search_element((By.XPATH, '//section[1]/span[1]/button'))
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
    def subscribe_to_user_list(self, timeout=Subscribe.timeout,
                               scatter_timeout=Subscribe.scatter_timeout,
                               subscribe_in_session=Subscribe.subscribe_in_session,
                               sleep_between_iterations=Subscribe.sleep_between_iterations,
                               operating_mode=Subscribe.operating_mode
                               ):
        """
        user_list - список юзеров для подписки
        timeout - среднее время на одну подписку
        scatter_timeout - разброс при вычислении таймаута
        sleep_between_iterations - дополнительный таймаут на каждые subscribe_in_session подписок
        limit_subscribes - максимальное число подписчиков у профиля (если больше, то пропустит этот профиль)
        """
        browser = self.browser
        user_list, ignore_list = set(), set()
        subscribe_count = 1
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
        elif operating_mode == 3:
            print('Открываю список "User_urls_subscribers"')
            path = 'data/User_urls_subscribers.txt'

        with open(path, 'r') as file:
            for link in file:
                user_list.add(link)
        with open('data/ignore_list.txt', 'r') as file:
            for link in file:
                ignore_list.add(link)
        with open('data/assert_log.txt', 'a') as file:
            file.write(f'{datetime.now().strftime("%H:%M:%S")} - лог файл запущен.')
        print(f'Профилей в списке до взаимодействия с игнор-листом - {len(user_list)}', end=', ')
        user_list = user_list.difference(ignore_list)
        print(f'после - {len(user_list)}')
        for user in user_list:
            try:
                if subscribe_count % subscribe_in_session == 0:
                    print(f'{datetime.now().strftime("%H:%M")} Подписался на очередные',
                          f'{subscribe_in_session} пользователей. Таймаут {sleep_between_iterations} минут.')

                    # исключает повторное срабатывание тайм-аута на первой итерации при срабатвании assert
                    subscribe_count += 0.1

                    with open('data/ignore_list.txt', 'r') as file:
                        for link in file:
                            ignore_list.add(link)
                    user_list = user_list.difference(ignore_list)
                    print(f'============ Осталось профилей для подписки - {len(user_list)} ============')
                    time.sleep(sleep_between_iterations * 60)

                browser.get(user)
                user_name = user.split("/")[-2]
                print(f'Перешёл в профиль: {user_name}')

                self.assert_subscribe()

                time.sleep(random.randrange(timeout - scatter_timeout, timeout + scatter_timeout))
                subscribe_button = self.search_element((By.XPATH, '//div/div/div/span/span[1]/button'))
                subscribe_button.click()

                assert self.should_be_subscribe_blocking(), 'Subscribe blocking'

                with open('data/ignore_list.txt', 'a') as file:
                    file.write(user)
                subscribe_count = int(subscribe_count) + 1
                print(
                    f'{datetime.now().strftime("%H:%M:%S")} Подписок: {subscribe_count - 1} подписался на: {user_name}',
                    end='  ======>')

            except TimeoutException:
                print('----TimeoutException---- переход к следующему посту.')
                continue

            except NoSuchElementException:
                print('----NoSuchElementException---- переход к следующему посту.')
                continue

            except AssertionError as assertion:
                with open('data/ignore_list.txt', 'a') as file:
                    file.write(user)
                assertion = str(assertion.args)
                if 'Subscribe blocking' in assertion:
                    print('======================МИКРОБАН ПОДПИСКИ======================')
                    break
                text = re.sub("[)(']", '', assertion)
                assert_log = f'{str(text)} ===> {user.split("/")[-2]} \n'
                with open('data/assert_log.txt', 'a') as file:
                    file.write(assert_log)
                print(f'{datetime.now().strftime("%H:%M:%S")}', text[:-1], end='======>')
                time.sleep(2)
                continue


operating_status = input('Укажите режим работы: ')
my_bot = FunctionClass(username, password, proxy=StartSettings.proxy, headless=StartSettings.headless)

try:
    my_bot.login()
    if operating_status == 'sub':
        my_bot.subscribe_to_user_list()
    elif operating_status == 'uns':
        my_bot.unsubscribe_for_all_users()
finally:
    my_bot.close_browser()
