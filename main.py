from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from module.support_funtion import SupportClass
from datetime import datetime
from data import *
from settings import *
import traceback
import random
import time
import re


class FunctionClass(SupportClass):
    # отписка от всех
    def unsubscribe_for_all_users(self,
                                  min_sleep=Unsubscribe.min_sleep,
                                  max_sleep=Unsubscribe.max_sleep,
                                  sleep_between_iterations=Unsubscribe.sleep_between_iterations,
                                  ):
        """
        min_sleep - минимальная задежка между отписками
        max_sleep - максимальная задержка между отписками
        sleep_between_iterations - таймаут между итерациями (по 10 отписок за итерацию)
        error_max - колличество ошибок, которые пропуустит цикл. После превышения - остановка.
        """
        browser = self.browser
        count_restart = 0
        browser.get(f"https://www.instagram.com/{username}/")

        while count_restart < 10:
            try:
                following_count = self.search_element((
                    By.XPATH, '//main/div/header/section/ul/li[3]/a/span'),
                    type_wait=ec.presence_of_element_located).text
                print(f"Количество подписок: {following_count}")
                count = 10
                browser.get(f"https://www.instagram.com/{username}/")

                following_button = self.search_element((By.XPATH, "//li[3]/a"))
                following_button.click()

                following_div_block = self.search_element((By.XPATH, "/html/body/div[6]/div/div/div[3]/ul/div"))
                time.sleep(2)
                following_users = following_div_block.find_elements(By.TAG_NAME, "li")

                for user in following_users:
                    if not count:
                        time.sleep(sleep_between_iterations)
                        break

                    unsubscribe_button = user.find_element(By.TAG_NAME, "button")
                    unsubscribe_button.click()
                    time.sleep(random.randrange(min_sleep, max_sleep))
                    self.search_element((By.CSS_SELECTOR, "button.-Cab_")).click()

                    print(f"Итерация #{count} >>> Отписался от пользователя  {datetime.now().strftime('%H:%M:%S')}")
                    count -= 1
            except TimeoutException:
                print('----TimeoutException----')
                count_restart += 1
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
            except AssertionError:
                print('----------- Лайк уже есть, переход к следующему посту. -----------')
                continue

    # подписыватеся на юзеров из списка, если нет списка, то вызывает "select_commentators"
    def subscribe_to_user_list(self, timeout=Subscribe.timeout,
                               scatter_timeout=Subscribe.scatter_timeout,
                               subscribe_in_session=Subscribe.subscribe_in_session,
                               sleep_between_iterations=Subscribe.sleep_between_iterations,
                               subscribe_limit=Subscribe.subscribe_limit_stop
                               ):
        """
        user_list - список юзеров для подписки
        timeout - среднее время на одну подписку
        scatter_timeout - разброс при вычислении таймаута
        sleep_between_iterations - дополнительный таймаут на каждые subscribe_in_session подписок
        limit_subscribes - максимальное число подписчиков у профиля (если больше, то пропустит этот профиль)
        subscribe_limit - колличество подписок в задаче
        """
        browser = self.browser
        user_list, ignore_list = set(), set()
        stop_word = 'Стоп-слово не присвоено на этапе модуля.'
        subscribe_count = 1
        self.file_read('User_urls_subscribers', user_list)
        self.file_read('ignore_list', ignore_list)
        self.file_write('assert_log', f'\n{datetime.now().strftime("%H:%M:%S")} - лог файл запущен. \n')
        print(f'Профилей в списке до взаимодействия с игнор-листом - {len(user_list)}', end=', ')
        user_list = user_list.difference(ignore_list)
        print(f'после - {len(user_list)}')
        for user in user_list:
            try:
                if subscribe_count == subscribe_limit:
                    print('======================ПОДПИСКА ЗАВЕРШЕНА======================')
                    break
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
                # поиск стоп-слов в биографии, если нашёл, то вернёт слово и уронит assert
                flag_and_stop_word = self.should_be_stop_word_in_biography(stop_words=Subscribe.stop_word_dict)
                flag, stop_word = flag_and_stop_word[0], flag_and_stop_word[1]
                assert flag, 'СТОП-СЛОВО'   # assert-функции, вывод которых прописан КАПСОМ - пишутся в лог файл

                time.sleep(random.randrange(timeout - scatter_timeout, timeout + scatter_timeout))
                subscribe_button = self.search_element((By.CSS_SELECTOR, 'span.vBF20._1OSdk > button'))
                subscribe_button.click()

                assert self.should_be_subscribe_blocking(), 'Subscribe blocking'

                self.file_write('ignore_list', user)

                subscribe_count = int(subscribe_count) + 1
                print(f'{datetime.now().strftime("%H:%M:%S")} == +  {user_name} == подписок: {subscribe_count - 1}',
                      end='  ======> ')

            except TimeoutException:
                traceback_text = traceback.format_exc()
                date = datetime.now().strftime("%d-%m %H:%M:%S")
                self.file_write('traceback_subscribe', date, traceback_text)
                print('----TimeoutException---- переход к следующему посту.', end=' ======> ')
                continue

            except NoSuchElementException:
                traceback_text = traceback.format_exc()
                date = datetime.now().strftime("%d-%m %H:%M:%S")
                self.file_write('traceback_subscribe', date, traceback_text)
                print('----NoSuchElementException---- переход к следующему посту.', end=' ======> ')
                continue

            except AssertionError as assertion:
                self.file_write('ignore_list', user)
                assertion = str(assertion.args)
                text = re.sub("[)(']", '', assertion)
                if 'Subscribe blocking' in assertion:
                    print('======================МИКРОБАН ПОДПИСКИ======================')
                    break
                # ловит стоп-слово, с которым упал assert и подставляет его в лог
                if 'СТОП-СЛОВО' in text:
                    assert_log = f'{str(stop_word)} ===> {user.split("/")[-2]} \n'
                    self.file_write('assert_log', assert_log)
                elif 'ПРОФИЛЬ "ПОМОЙКА".' in text:
                    assert_log = f'ПРОФИЛЬ "ПОМОЙКА" ===> {user.split("/")[-2]} \n'
                    self.file_write('assert_log', assert_log)

                print(f'{datetime.now().strftime("%H:%M:%S")} ==   ', text[:-1], end=' ======> ')
                time.sleep(2)
                continue


operating_status = input('Укажите режим работы: ')
headless_and_proxy = input('Headless(y/n) Proxy(y/n): ')
my_bot = FunctionClass(username, password, headless_and_proxy)

try:
    my_bot.login()
    if operating_status == 'sub':
        my_bot.subscribe_to_user_list()
    elif operating_status == 'uns':
        my_bot.unsubscribe_for_all_users()
    elif operating_status == 'sel':
        my_bot.select_subscribes()
finally:
    my_bot.close_browser()
