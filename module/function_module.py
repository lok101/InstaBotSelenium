from module.base_module import ActivBlocking
from selenium.webdriver.support import expected_conditions as ec
from module.message_text_module import ErrorMessage
from selenium.webdriver.common.by import By
from module.filter_module import FilterClass
from datetime import datetime
from settings import *
import random
import time


class FunctionClass(FilterClass):
    # отписка от всех
    def unsubscribe_for_all_users(self):

        min_sleep = Unsubscribe.min_sleep
        max_sleep = Unsubscribe.max_sleep
        sleep_between_iterations = Unsubscribe.sleep_between_iterations
        """
        min_sleep - минимальная задержка между отписками
        max_sleep - максимальная задержка между отписками
        sleep_between_iterations - таймаут между итерациями (по 10 отписок за итерацию)
        """
        self.mode = 'unsubscribe'

        while self.count_iteration < 20:
            try:
                count = 10
                self.go_to_my_profile_page()

                if self.subscribe == 0:
                    print('= = = = ОТПИСКА ЗАВЕРШЕНА = = = =')
                    break

                following_button = self.search_element((By.XPATH, "//li[3]/a"))
                following_button.click()

                following_div_block = self.search_element((By.CSS_SELECTOR, "div > div > div.isgrP > ul > div"))
                time.sleep(2)
                following_users = following_div_block.find_elements(By.TAG_NAME, "li")

                for user_unsubscribe in following_users:
                    if not count:
                        time.sleep(sleep_between_iterations)
                        break

                    unsubscribe_button = user_unsubscribe.find_element(By.TAG_NAME, "button")
                    unsubscribe_button.click()
                    time.sleep(random.randrange(min_sleep - 2, max_sleep - 2))
                    self.search_element((By.CSS_SELECTOR, "button.-Cab_")).click()
                    assert self.should_be_subscribe_and_unsubscribe_blocking(), ErrorMessage.unsubscribe_blocking

                    print(f"{datetime.now().strftime('%H:%M:%S')}. Итерация #{count}")
                    count -= 1

            except AssertionError as assertion:
                self.exception_text = str(assertion.args)
                self.print_log_assert_and_control_cycle()

            except Exception as ex:
                self.exception_text = str(type(ex)).split("'")[1].split('.')[-1]
                self.print_and_save_log_traceback()
                self.count_iteration += 1
                continue

    def short_subscribe(self):
        try:
            self.mode = 'short_subscribe'
            self.min_timeout = ShortSubscribe.min_timeout
            self.max_timeout = ShortSubscribe.max_timeout
            self.count_iteration = int(str(self.cycle) + str(0))
            self.count_limit = (self.cycle + 1) * ShortSubscribe.subscribe_in_session
            user_list = self.difference_sets('filtered/user_urls_subscribers.txt', 'ignore_list.txt')
            self.go_to_my_profile_page()

        except AssertionError as assertion:
            self.exception_text = str(assertion.args)
            self.print_log_assert_and_control_cycle()

        except Exception as ex:
            self.exception_text = str(type(ex)).split("'")[1].split('.')[-1]
            self.print_and_save_log_traceback()

        for self.user_url in user_list:
            try:
                self.go_to_user_page()
                self.press_to_button_subscribe()

                if self.count_iteration >= self.count_limit:
                    user_list = self.difference_sets('filtered/user_urls_subscribers.txt', 'ignore_list.txt')
                    print(f'Подписался на {self.count_limit} профилей. Перехожу в следующий аккаунт.',
                          f'Осталось профилей - {len(user_list)}')
                    break

            except AssertionError as assertion:
                self.exception_text = str(assertion.args)
                self.print_log_assert_and_control_cycle()

            except Exception as ex:
                self.exception_text = str(type(ex)).split("'")[1].split('.')[-1]
                self.print_and_save_log_traceback()
                continue

    # подписывается на юзеров из файла
    def subscribe_to_user_list(self):
        """
        subscribe_in_session - количество подписок в одном заходе.
        sleep_between_iterations - таймаут на каждые subscribe_in_session подписок.
        self.count_limit - количество подписок в задаче.
        """
        self.mode = 'subscribe'

        subscribe_in_session = Subscribe.subscribe_in_session
        sleep_between_iterations = Subscribe.sleep_between_iterations
        subscribe_limit_stop = Subscribe.subscribe_limit_stop
        self.min_timeout = Subscribe.min_timeout
        self.max_timeout = Subscribe.max_timeout
        self.count_iteration = 0
        user_list = self.difference_sets('filtered/user_urls_subscribers.txt', 'ignore_list.txt')
        self.go_to_my_profile_page()
        self.count_limit = subscribe_limit_stop - self.subscribe

        for self.user_url in user_list:
            try:
                self.go_to_user_page()
                self.press_to_button_subscribe()

                if self.count_iteration >= self.count_limit:
                    print('= = = = ПОДПИСКА ЗАВЕРШЕНА = = = =')
                    break

                if self.count_iteration % subscribe_in_session == 0 and self.count_iteration != 0:
                    self.go_to_my_profile_page(end_str=' ')
                    print(f'{datetime.now().strftime("%H:%M:%S")} Подписался на очередные',
                          f'{subscribe_in_session} пользователей. Таймаут {sleep_between_iterations} минут.')

                    user_list = self.difference_sets('filtered/user_urls_subscribers.txt', 'ignore_list.txt')
                    print(f'= = = = Осталось профилей для подписки - {len(user_list)} = = = =')
                    time.sleep(sleep_between_iterations * 60)

            except AssertionError as assertion:
                self.exception_text = str(assertion.args)
                self.print_log_assert_and_control_cycle()

            except Exception as ex:
                self.exception_text = str(type(ex)).split("'")[1].split('.')[-1]
                self.print_and_save_log_traceback()
                continue

    # фильтрует список профилей
    def filter_user_list(self):

        self.mode = 'filtered'
        count_user_in_session = 0
        self.count_limit = 30

        self.file_write('logs/assert_stop_word_log.txt', f'\n{datetime.now().strftime("%d-%m %H:%M:%S")} - старт.\n')
        self.file_write('logs/assert_bad_profile_log.txt', f'\n{datetime.now().strftime("%d-%m %H:%M:%S")} - старт.\n')

        while True:
            try:
                user_list = self.difference_sets(
                    'non_filtered/user_urls_subscribers.txt',
                    'ignore_list.txt',
                    'filtered/user_urls_subscribers.txt'
                )
                user_list_count = len(self.difference_sets(
                    'filtered/user_urls_subscribers.txt',
                    'ignore_list.txt'
                ))
                print(
                    f'\nНе отфильтровано - <<<{len(user_list)}>>>. Готовых - {user_list_count}.',
                    f'Отобрано в сессии - {count_user_in_session}.\n')

                for i in range(self.count_limit):
                    self.user_url = user_list.pop()
                    self.count_iteration = i
                    try:
                        self.go_to_user_page()
                        self.should_be_compliance_with_limits()
                        self.file_write('filtered/user_urls_subscribers.txt', self.user_url)
                        count_user_in_session += 1
                        print('Подходит.')

                    except AssertionError as assertion:
                        self.exception_text = str(assertion.args)
                        self.print_log_assert_and_control_cycle()

                    except Exception as ex:
                        self.exception_text = str(type(ex)).split("'")[1].split('.')[-1]
                        self.print_and_save_log_traceback()
                        continue

            except ActivBlocking:
                print('= = = = МИКРОБАН АКТИВНОСТИ = = = =')
                break

    # собирает пользователей "по конкуренту" со списка ссылок
    def select_subscribers(self, iter_count):

        scroll_number_subscribers_list = SearchUser.scroll_number_subscribers_list

        self.mode = 'selection'
        urls_public = []
        self.file_read(self.read_file_path, urls_public)
        self.count_iteration = iter_count * 10
        self.count_limit = len(urls_public)
        print(f'= = = = Итерация сбора {iter_count + 1} из {len(urls_public) // 10}. = = = =')
        urls_public = urls_public[int(str(iter_count) + '0'):int(str(iter_count + 1) + '0')]
        for self.user_url in urls_public:
            try:
                self.go_to_user_page()
                self.count_iteration += 1
                subscribes_button = self.search_element((By.CSS_SELECTOR, 'li:nth-child(2) > a'))
                subscribes_button.click()

                subscribes_ul = self.search_element((By.CSS_SELECTOR, 'div.RnEpo.Yx5HN > div > div > div> div.isgrP'),
                                                    type_wait=ec.presence_of_element_located)
                for i in range(scroll_number_subscribers_list + 1):
                    self.browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", subscribes_ul)
                    self.search_element((By.CSS_SELECTOR, 'li div svg.By4nA'), timeout=10,
                                        type_wait=ec.invisibility_of_element_located)
                    time.sleep(0.5)
                    self.search_element((By.CSS_SELECTOR, 'li div svg.By4nA'), timeout=10,
                                        type_wait=ec.invisibility_of_element_located)
                    time.sleep(0.5)

                user_urls = self.tag_search(ignore=self.username)
                self.file_write(self.write_file_path, user_urls)
                with open(f'data/{self.write_file_path}', 'r') as file:
                    size = len(file.readlines())
                    print(f'Успешно. Количество собранных пользователей: {size}.')

            except AssertionError as assertion:
                self.exception_text = str(assertion.args)
                self.print_log_assert_and_control_cycle()

            except Exception as ex:
                self.exception_text = str(type(ex)).split("'")[1].split('.')[-1]
                self.print_and_save_log_traceback()
                continue
