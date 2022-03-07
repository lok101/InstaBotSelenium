from selenium.webdriver.support import expected_conditions as ec
from module.exception_module import FilteredOut, BotNonCriticalException
from module.filter_module import FilterClass
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime
from settings import *
import random
import time


class FunctionClass(FilterClass):
    def login(self):
        while True:
            try:
                try:
                    try:
                        self.browser = webdriver.Chrome(options=self.chrome_options)
                        if self.proxy:
                            self.check_proxy_ip()
                        self.browser.get(self.link)
                        self.should_be_home_page()
                        self.cookie_login()
                        break

                    except FileNotFoundError:
                        self.not_cookie_login()
                        break

                except Exception as exception:
                    self.exception = exception
                    self.standard_exception_handling()
                    break
            except ConnectionError:
                continue

    # отписка от всех
    def unsubscribe(self):
        while self.count_iteration < 20:
            try:
                count = 10
                self.go_to_my_profile_page()

                if self.followers == 0:
                    print('= = = = ОТПИСКА ЗАВЕРШЕНА = = = =')
                    break

                following_button = self.search_element((By.XPATH, "//li[3]/a"))
                following_button.click()

                following_div_block = self.search_element((By.CSS_SELECTOR, "div > div > div.isgrP > ul > div"))
                time.sleep(2)
                following_users = following_div_block.find_elements(By.TAG_NAME, "li")

                for user_unsubscribe in following_users:
                    if not count:
                        time.sleep(Unsubscribe.sleep_between_iterations * 60)
                        break

                    unsubscribe_button = user_unsubscribe.find_element(By.TAG_NAME, "button")
                    unsubscribe_button.click()
                    time.sleep(random.randrange(Unsubscribe.min_sleep - 2, Unsubscribe.max_sleep - 2))
                    self.search_element((By.CSS_SELECTOR, "button.-Cab_")).click()
                    self.should_be_subscribe_and_unsubscribe_blocking()

                    print(f"{datetime.now().strftime('%H:%M:%S')} Итерация #{count}")
                    count -= 1

            except BotNonCriticalException as exception:
                self.exception = exception
                self.catching_non_critical_bot_exceptions()

            except Exception as exception:
                self.exception = exception
                self.standard_exception_handling()
                self.count_iteration += 1

    # подписывается на юзеров из файла
    def subscribe(self):
        user_list = self.difference_sets('filtered/user_urls_subscribers.txt', 'ignore_list.txt')
        self.go_to_my_profile_page()
        self.count_limit = Subscribe.subscribe_limit_stop - self.followers

        for self.user_url in user_list:
            try:
                self.go_to_user_page()
                self.press_to_button_subscribe()

                if self.count_iteration >= self.count_limit:
                    print('= = = = ПОДПИСКА ЗАВЕРШЕНА = = = =')
                    break

                if self.count_iteration % Subscribe.subscribe_in_session == 0 and self.count_iteration != 0:
                    self.go_to_my_profile_page(end_str=' ')
                    print(f'{datetime.now().strftime("%H:%M:%S")} Подписался на очередные',
                          f'{Subscribe.subscribe_in_session} пользователей. ',
                          f'Таймаут {Subscribe.sleep_between_iterations} минут.')

                    user_list = self.difference_sets('filtered/user_urls_subscribers.txt', 'ignore_list.txt')
                    print(f'= = = = Осталось профилей для подписки - {len(user_list)} = = = =')
                    time.sleep(Subscribe.sleep_between_iterations * 60)

            except BotNonCriticalException as exception:
                self.exception = exception
                self.catching_non_critical_bot_exceptions()

            except Exception as exception:
                self.exception = exception
                self.standard_exception_handling()

    # фильтрует список профилей
    def filter(self):

        count_user_in_session = 0
        self.count_limit = 30

        while True:
            user_list = self.difference_sets(
                'non_filtered/subscribers_urls.txt',
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
                try:
                    self.user_url = user_list.pop()
                    self.count_iteration = i
                    self.go_to_user_page()
                    self.should_be_compliance_with_limits()
                    self.file_write('filtered/user_urls_subscribers.txt', self.user_url)
                    count_user_in_session += 1
                    print('Подходит.')

                except BotNonCriticalException as exception:
                    self.exception = exception
                    self.catching_non_critical_bot_exceptions()

                except FilteredOut as exception:
                    self.exception = exception
                    self.bot_filter_out_handling()

                except Exception as exception:
                    self.exception = exception
                    self.standard_exception_handling()

                finally:
                    time.sleep(Filtered.timeout)

    # собирает пользователей "по конкуренту" со списка ссылок
    def parce(self):

        urls_public = []
        self.file_read(self.read_file_path, urls_public)
        self.count_limit = len(urls_public)
        urls_public = urls_public[self.count_iteration:-1]

        for self.user_url in urls_public:
            try:
                self.go_to_user_page()
                self.count_iteration += 1
                subscribes_button = self.search_element((By.CSS_SELECTOR, 'li:nth-child(2) > a'))
                subscribes_button.click()

                subscribes_ul = self.search_element((By.CSS_SELECTOR, 'div.RnEpo.Yx5HN > div > div > div> div.isgrP'),
                                                    type_wait=ec.presence_of_element_located)
                for i in range(SearchUser.scroll_number_subscribers_list + 1):
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

            except BotNonCriticalException as exception:
                self.exception = exception
                self.catching_non_critical_bot_exceptions()

            except Exception as exception:
                self.exception = exception
                self.standard_exception_handling()
