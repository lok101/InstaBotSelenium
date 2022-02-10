from module.base_module import ActivBlocking
from selenium.webdriver.support import expected_conditions as ec
from module.message_text_module import ErrorMessage, FilterMessage
from selenium.webdriver.common.by import By
from module.filter_module import FilterClass
from datetime import datetime
from settings import *
import random
import time


class FunctionClass(FilterClass):
    # отписка от всех
    def unsubscribe_for_all_users(self,
                                  min_sleep=Unsubscribe.min_sleep,
                                  max_sleep=Unsubscribe.max_sleep,
                                  sleep_between_iterations=Unsubscribe.sleep_between_iterations,
                                  ):
        """
        min_sleep - минимальная задержка между отписками
        max_sleep - максимальная задержка между отписками
        sleep_between_iterations - таймаут между итерациями (по 10 отписок за итерацию)
        """
        self.mode = 'unsubscribe'

        while self.count_iteration < 20:
            try:
                count = 10
                following_count = self.go_to_my_profile_page()

                if following_count == 0:
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
                assertion_text = str(assertion.args)
                if ErrorMessage.unsubscribe_blocking in assertion_text:
                    print('= = = = МИКРОБАН ОТПИСКИ = = = =')
                    break
                elif ErrorMessage.activiti_blocking in assertion_text:
                    print('= = = = МИКРОБАН АКТИВНОСТИ = = = =')
                    break
                elif ErrorMessage.page_loading_error in assertion_text:
                    sleep = StartSettings.sleep_page_not_found
                    print(f'Страница не загрузилась. Жду {sleep} секунд.')
                    time.sleep(sleep)
                    continue
                else:
                    print('!!! Неизвестный Assert !!!')

            except Exception as ex:
                ex_type = str(type(ex)).split("'")[1].split('.')[-1]
                self.print_and_save_log_traceback(ex_type)
                self.count_iteration += 1
                continue

    # подписывается на юзеров из файла
    def subscribe_to_user_list(self, subscribe_in_session=Subscribe.subscribe_in_session,
                               sleep_between_iterations=Subscribe.sleep_between_iterations,
                               subscribe_limit=Subscribe.subscribe_limit_stop
                               ):
        """
        subscribe_in_session - количество подписок в одном заходе.
        sleep_between_iterations - таймаут на каждые subscribe_in_session подписок.
        subscribe_limit - количество подписок в задаче.
        """
        self.mode = 'subscribe'
        user_list = self.difference_sets('filtered/user_urls_subscribers', 'filtered/user_urls_subscribers')
        subs = self.go_to_my_profile_page()

        for user_url in user_list:
            try:
                self.go_to_user_page(user_url)
                self.press_to_button_subscribe(user_url)

                if subs + self.count_iteration >= subscribe_limit:
                    print('= = = = ПОДПИСКА ЗАВЕРШЕНА = = = =')
                    break

                if self.count_iteration % subscribe_in_session == 0:
                    subs = self.go_to_my_profile_page()
                    print(f'{datetime.now().strftime("%H:%M:%S")} Подписался на очередные',
                          f'{subscribe_in_session} пользователей. Всего подписок - {subs}.',
                          f'Таймаут {sleep_between_iterations} минут.')

                    self.count_iteration = 0.1
                    user_list = self.difference_sets('filtered/user_urls_subscribers', 'filtered/user_urls_subscribers')
                    print(f'= = = = Осталось профилей для подписки - {len(user_list)} = = = =')
                    time.sleep(sleep_between_iterations * 60)

            except AssertionError as assertion:
                assertion_text = str(assertion.args)
                if ErrorMessage.subscribe_blocking in assertion_text:
                    print('= = = = МИКРОБАН ПОДПИСКИ = = = =')
                    break
                elif ErrorMessage.activiti_blocking in assertion_text:
                    print('= = = = МИКРОБАН АКТИВНОСТИ = = = =')
                    break
                elif ErrorMessage.page_not_found in assertion_text:
                    print('Страница больше недоступна.')
                    self.file_write('ignore_list', user_url)
                    continue
                elif ErrorMessage.page_loading_error in assertion_text:
                    sleep = StartSettings.sleep_page_not_found
                    print(f'Страница не загрузилась. Жду {sleep} секунд.')
                    time.sleep(sleep)
                    continue
                else:
                    print('!!! Неизвестный Assert !!!')

            except Exception as ex:
                self.count_iteration += 0.1
                ex_type = str(type(ex)).split("'")[1].split('.')[-1]
                self.print_and_save_log_traceback(ex_type)
                continue

    # фильтрует список профилей
    def filter_user_list(self, timeout=StartSettings.filtered_user_list_timeout):
        self.mode = 'filtered'
        stop_word = 'Стоп-слово не присвоено на этапе модуля.'
        count_user_in_session = 0
        self.count_iteration = 30

        self.file_write('logs/assert_stop_word_log', f'\n{datetime.now().strftime("%d-%m %H:%M:%S")} - старт.\n')
        self.file_write('logs/assert_bad_profile_log', f'\n{datetime.now().strftime("%d-%m %H:%M:%S")} - старт.\n')

        while True:
            try:
                user_list = self.difference_sets(
                    'non_filtered/user_urls_subscribers',
                    'ignore_list',
                    'filtered/user_urls_subscribers'
                )
                user_list_count = len(self.difference_sets(
                    'filtered/user_urls_subscribers',
                    'ignore_list'
                ))
                print(
                    f'Не отфильтровано - <<<{len(user_list)}>>>. Готовых - {user_list_count}.',
                    f'Отобрано в сессии - {count_user_in_session}.')

                for i in range(self.count_iteration):
                    user_url = user_list.pop()
                    try:
                        self.go_to_user_page(user_url)

                        self.should_be_compliance_with_limits(max_coefficient=Subscribe.coefficient_subscribers,
                                                              posts_max=Subscribe.posts_max,
                                                              posts_min=Subscribe.posts_min,
                                                              subscribers_max=Subscribe.subscribers_max,
                                                              subscribers_min=Subscribe.subscribers_min,
                                                              subscriptions_max=Subscribe.subscriptions_max,
                                                              subscriptions_min=Subscribe.subscriptions_min,
                                                              break_limit=Subscribe.break_limit)

                        # поиск стоп-слов в биографии, если нашёл, то вернёт слово и уронит assert
                        flag_and_stop_word = self.should_be_stop_word_in_biography(stop_words=Subscribe.stop_word_dict)
                        flag, stop_word = flag_and_stop_word[0], flag_and_stop_word[1]
                        assert flag, FilterMessage.stop_word

                        self.file_write('filtered/user_urls_subscribers', user_url)
                        count_user_in_session += 1

                        print(f'Подходит. [{i + 1}/{self.count_iteration}]')

                    except AssertionError as assertion:
                        assertion_text = str(assertion.args)
                        if ErrorMessage.activiti_blocking in assertion_text:
                            raise ActivBlocking
                        elif ErrorMessage.page_not_found in assertion_text:
                            print('Страница больше недоступна.')
                            self.file_write('ignore_list', user_url)
                            continue
                        elif ErrorMessage.page_loading_error in assertion_text:
                            sleep = StartSettings.sleep_page_not_found
                            print(f'Страница не загрузилась. Жду {sleep} секунд.')
                            time.sleep(sleep)
                            continue
                        elif FilterMessage.stop_word in assertion_text:
                            assert_log = f'{str(stop_word)} ===> {user_url}'
                            self.file_write('logs/assert_stop_word_log', assert_log)
                            self.file_write('ignore_list', user_url)
                            print(f'{FilterMessage.stop_word} [{i + 1}/{self.count_iteration}]')
                            time.sleep(timeout)
                            continue
                        elif FilterMessage.bad_profile in assertion_text:
                            assert_log = f'{user_url}'
                            self.file_write('logs/assert_bad_profile_log', assert_log)
                            self.file_write('ignore_list', user_url)
                            print(f'{FilterMessage.bad_profile} [{i + 1}/{self.count_iteration}]')
                            time.sleep(timeout)
                            continue

                    except Exception as ex:
                        ex_type = str(type(ex)).split("'")[1].split('.')[-1]
                        self.print_and_save_log_traceback(ex_type)
                        continue

            except ActivBlocking:
                print('= = = = МИКРОБАН АКТИВНОСТИ = = = =')
                break

            except KeyError:
                print('= = = = ФИЛЬТРАЦИЯ ЗАВЕРШЕНА = = = =')
                break

    # собирает пользователей "по конкуренту" со списка ссылок
    def select_subscribers(self, iter_count, scroll_number_subscribers_list=SearchUser.scroll_number_subscribers_list):
        self.mode = 'selection'
        urls_public = []
        self.file_read('url_lists/public_url_for_subscribe', urls_public)
        print(f'= = = = Итерация сбора {iter_count + 1} из {len(urls_public) // 10}. = = = =')
        urls_public = urls_public[int(str(iter_count) + '0'):int(str(iter_count + 1) + '0')]
        for user_url in urls_public:
            try:
                self.go_to_user_page(user_url)
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
                self.file_write('non_filtered/user_urls_subscribers', user_urls)
                with open('data/non_filtered/user_urls_subscribers.txt', 'r') as file:
                    size = len(file.readlines())
                    print(f'Успешно. Количество собранных пользователей: {size}.')

            except AssertionError as assertion:
                assertion_text = str(assertion.args)
                if ErrorMessage.activiti_blocking in assertion_text:
                    print('Микробан активности. Добавлена запись в лог.')
                    date = datetime.now().strftime("%d-%m %H:%M:%S")
                    log = f'{date} -- {self.username}\n'
                    self.file_write('selection/authorize_error', log)
                    break
                elif ErrorMessage.page_not_found in assertion_text:
                    print('Страница больше недоступна по этому адресу. Добавлена запись в лог.')
                    date = datetime.now().strftime("%d-%m %H:%M:%S")
                    log = f'{date} -- {user_url}\n'
                    self.file_write('selection/invalid_url', log)
                    continue
                elif ErrorMessage.page_loading_error in assertion_text:
                    sleep = StartSettings.sleep_page_not_found
                    print(f'Страница не загрузилась. Жду {sleep} секунд.')
                    time.sleep(sleep)
                    continue
                else:
                    print('!!! Неизвестный Assert !!!')
                continue

            except Exception as ex:
                ex_type = str(type(ex)).split("'")[1].split('.')[-1]
                self.print_and_save_log_traceback(ex_type)
                continue
