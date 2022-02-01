from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, \
    WebDriverException
from module.base_module import LoginError
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import data
from module.filter_module import FilterClass
from datetime import datetime
from settings import *
from data import tag_list
import traceback
import random
import time
import re


class FunctionClass(FilterClass):
    # отписка от всех
    def unsubscribe_for_all_users(self, username,
                                  min_sleep=Unsubscribe.min_sleep,
                                  max_sleep=Unsubscribe.max_sleep,
                                  sleep_between_iterations=Unsubscribe.sleep_between_iterations,
                                  ):
        """
        min_sleep - минимальная задержка между отписками
        max_sleep - максимальная задержка между отписками
        sleep_between_iterations - таймаут между итерациями (по 10 отписок за итерацию)
        error_max - количество ошибок, которые пропустит цикл. После превышения - остановка.
        """
        browser = self.browser
        count_restart = 0
        browser.get(f"https://www.instagram.com/{username}/")

        while count_restart < 20:
            try:
                browser.get(f"https://www.instagram.com/{username}/")
                assert self.should_be_error_connection_page(), 'Ошибка загрузки страницы.'
                assert self.should_be_activity_blocking(), 'Микробан активности.'
                following_count = self.search_element((
                    By.XPATH, '//main/div/header/section/ul/li[3]/a/span'),
                    type_wait=ec.presence_of_element_located).text
                print(f"Количество подписок: {following_count}")
                count = 10

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
                    time.sleep(random.randrange(min_sleep, max_sleep))
                    self.search_element((By.CSS_SELECTOR, "button.-Cab_")).click()

                    print(f"Итерация #{count} >>> Отписался от пользователя  {datetime.now().strftime('%H:%M:%S')}")
                    count -= 1
            except TimeoutException:
                print('----TimeoutException----')
                count_restart += 1
                continue

            except WebDriverException:
                print('>> WebDriverException <<')
                continue

            except AssertionError as assertion:
                if 'Ошибка загрузки страницы.' in assertion:
                    print('Ошибка загрузки страницы.')
                elif 'Микробан активности.' in assertion:
                    print('Микробан активности.')
                    break
                else:
                    print('!!! Неизвестный Assert !!!')
                continue

    # подписывается на юзеров из файла
    def subscribe_to_user_list(self, username, min_timeout=Subscribe.min_timeout,
                               max_timeout=Subscribe.max_timeout,
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
        subscribe_limit - количество подписок в задаче
        """
        browser = self.browser
        user_list, ignore_list = set(), set()
        subscribe_count = 0.1
        self.file_read('filtered/user_urls_subscribers', user_list)
        self.file_read('ignore_list', ignore_list)
        user_list = user_list.difference(ignore_list)
        browser.get(f"https://www.instagram.com/{username}/")
        assert self.should_be_activity_blocking(), 'Микробан активности.'
        subscribe = self.return_number_posts_subscribe_and_subscribers()[3]
        print(f'Профилей в списке - {len(user_list)}, подписок у аккаунта - {subscribe}')

        for user_subscribe in user_list:
            try:
                if subscribe + subscribe_count >= subscribe_limit:
                    print('======================ПОДПИСКА ЗАВЕРШЕНА======================')
                    break
                if subscribe_count % subscribe_in_session == 0:
                    browser.get(f"https://www.instagram.com/{username}/")
                    subscribe = self.return_number_posts_subscribe_and_subscribers()[3]
                    print(f'{datetime.now().strftime("%H:%M:%S")} Подписался на очередные',
                          f'{subscribe_in_session} пользователей. Всего подписок - {subscribe}.',
                          f'Таймаут {sleep_between_iterations} минут.')

                    subscribe_count = 0.1

                    self.file_read('ignore_list', ignore_list)
                    user_list = user_list.difference(ignore_list)
                    print(f'============ Осталось профилей для подписки - {len(user_list)} ============')
                    time.sleep(sleep_between_iterations * 60)

                browser.get(user_subscribe)
                user_name = user_subscribe.split("/")[-2]
                print(f'{datetime.now().strftime("%H:%M:%S")}-- <{username}> -- перешёл в профиль: {user_name}', end=' =====> ')

                button = self.press_to_button_subscribe()
                if button is not None:
                    button.click()
                    time.sleep(random.randrange(min_timeout, max_timeout))
                    assert self.should_be_subscribe_blocking(), 'Микробан подписки.'  # проверка на микробан
                    self.file_write('ignore_list', user_subscribe)
                    subscribe_count = int(subscribe_count) + 1
                    print(f'Успешно. Подписок: {subscribe_count}')
                else:
                    print('Кнопка не найдена.')

            except TimeoutException:
                traceback_text = traceback.format_exc()
                date = datetime.now().strftime("%d-%m %H:%M:%S")
                self.file_write('logs/traceback_subscribe', date, traceback_text)
                print('>> TimeoutException <<')
                continue

            except NoSuchElementException:
                subscribe_count += 0.1
                traceback_text = traceback.format_exc()
                date = datetime.now().strftime("%d-%m %H:%M:%S")
                self.file_write('logs/traceback_subscribe', date, traceback_text)
                print('>> TimeoutException <<')
                continue

            except StaleElementReferenceException:
                subscribe_count += 0.1
                traceback_text = traceback.format_exc()
                date = datetime.now().strftime("%d-%m %H:%M:%S")
                self.file_write('logs/traceback_subscribe', date, traceback_text)
                print('>> StaleElementReferenceException <<')
                continue

            except AssertionError as assertion:
                if 'Микробан активности.' in assertion:
                    print('====================== МИКРОБАН АКТИВНОСТИ ======================')
                    break
                elif 'Микробан подписки.' in assertion:
                    print('====================== МИКРОБАН ПОДПИСКИ ======================')
                    break
                else:
                    print('!!! Неизвестный Assert !!!')

            except WebDriverException:
                subscribe_count += 0.1
                print('>> WebDriverException <<')
                continue

    # фильтрует список профилей
    def filter_user_list(self, account_id, iteration_number, timeout=StartSettings.filtered_user_list_timeout):
        browser = self.browser
        user_urls, ignore_list, filtered_user = set(), set(), set()
        stop_word = 'Стоп-слово не присвоено на этапе модуля.'
        count_user_in_session = 0
        count_iteration = 0

        self.file_read('non_filtered/user_urls_subscribers', user_urls)
        self.file_read('ignore_list', ignore_list)
        self.file_read('filtered/user_urls_subscribers', filtered_user)
        self.file_write('logs/assert_stop_word_log', f'\n{datetime.now().strftime("%d-%m %H:%M:%S")} - старт.\n')
        self.file_write('logs/assert_bad_profile_log', f'\n{datetime.now().strftime("%d-%m %H:%M:%S")} - старт.\n')

        print(f'Профилей в списке до взаимодействия с игнор-листом - {len(user_urls)}', end=', ')
        user_list = user_urls.difference(ignore_list, filtered_user)
        print(f'после - {len(user_list)}')
        for user_filtered in user_list:
            urls_list = set()
            count_iteration += 1
            try:
                browser.get(user_filtered)
                user_name = user_filtered.split("/")[-2]
                print(f'{datetime.now().strftime("%H:%M:%S")} - {account_id} -- <Цикл - {iteration_number + 1}> \
                -- Перешёл в профиль: {user_name}',
                      end=' ======> ')

                assert self.should_be_user_page(), 'Страница не существует'
                self.should_be_compliance_with_limits(max_coefficient=Subscribe.coefficient_subscribers,
                                                      posts_max=Subscribe.posts_max, posts_min=Subscribe.posts_min,
                                                      subscribers_max=Subscribe.subscribers_max,
                                                      subscribers_min=Subscribe.subscribers_min,
                                                      subscriptions_max=Subscribe.subscriptions_max,
                                                      subscriptions_min=Subscribe.subscriptions_min,
                                                      break_limit=Subscribe.break_limit)

                # поиск стоп-слов в биографии, если нашёл, то вернёт слово и уронит assert
                flag_and_stop_word = self.should_be_stop_word_in_biography(stop_words=Subscribe.stop_word_dict)
                flag, stop_word = flag_and_stop_word[0], flag_and_stop_word[1]
                assert flag, 'СТОП-СЛОВО'  # assert-функции, вывод которых прописан КАПСОМ - пишутся в лог файл

                self.file_write('filtered/user_urls_subscribers', user_filtered)
                self.file_read('filtered/user_urls_subscribers', urls_list)
                count_user_in_session += 1
                user_list_count = len(urls_list.difference(ignore_list))

                print(f'Подходит.')
                print(f'Профилей в списке - {user_list_count}. \
                Отобрано в сессии - {count_user_in_session}. Перебрал - {count_iteration}')

            except AssertionError as assertion:
                assertion = str(assertion.args)
                text = re.sub("[)(']", '', assertion)

                if 'Subscribe blocking' in assertion:
                    print('======== МИКРОБАН АКТИВНОСТИ ========')
                    break
                elif 'Страница не существует' in assertion:
                    print('Страница не существует')
                    self.file_write('ignore_list', user_filtered)
                    continue
                elif 'Страница не загрузилась' in assertion:
                    print('Страница не загрузилась')

                self.file_write('ignore_list', user_filtered)
                # ловит стоп-слово, с которым упал assert и подставляет его в лог
                if 'СТОП-СЛОВО' in text:
                    assert_log = f'{str(stop_word)} ===> {user_filtered}'
                    self.file_write('logs/assert_stop_word_log', assert_log)
                elif 'ПРОФИЛЬ "ПОМОЙКА".' in text:
                    assert_log = f'{user_filtered}'
                    self.file_write('logs/assert_bad_profile_log', assert_log)

                print(text[:-1])
                time.sleep(timeout)
                continue

            except NoSuchElementException:
                traceback_text = traceback.format_exc()
                date = datetime.now().strftime("%d-%m %H:%M:%S")
                self.file_write('logs/traceback_filtered', date, traceback_text)
                print('>> NoSuchElementException <<')
                continue

            except TimeoutException:
                traceback_text = traceback.format_exc()
                date = datetime.now().strftime("%d-%m %H:%M:%S")
                self.file_write('logs/traceback_filtered', date, traceback_text)
                print('>> TimeoutException <<')
                continue

            except LoginError:
                print('= = = = = = = = Не получилось залогиниться. = = = = = = = =')
                continue

            except Exception:
                traceback_text = traceback.format_exc()
                date = datetime.now().strftime("%d-%m %H:%M:%S")
                self.file_write('logs/select', date, traceback_text)

    # собирает список тех, кто комментировал посты, для сбора ссылок на посты вызывает "select_url_posts_to_hashtag"
    def select_commentators(self, hashtag=tag_list[0],
                            number_scrolls=1,
                            scrolls_timeout=1,
                            ):
        """
        number_scrolls - количество прокруток поля комментариев у поста
        scrolls_timeout - задержка перед прокруткой (иначе может падать с ошибкой NoSuchElement)
        delete_file - если "yes", то очистит файл со ссылками перед записью
        """
        browser = self.browser
        link_list = self.select_url_posts_to_hashtag(hashtag=hashtag)
        for link in link_list:
            browser.get(link)
            comments_ul = self.search_element((By.XPATH, '//div[2]/div/div[2]/div[1]/ul'))

            for number in range(number_scrolls):
                time.sleep(2)
                browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", comments_ul)
                time.sleep(scrolls_timeout)

                plus_button = self.search_element((By.XPATH, '//div/div[2]/div[1]/ul/li/div/button'))
                plus_button.click()
                time.sleep(scrolls_timeout)

            # находит ссылку на профиль, опубликовавший запись, что бы кинуть его в игнор поиска по тегу
            block_profile = self.search_element((By.XPATH, '//header/div[2]/div[1]/div[1]/span/a'))
            name_profile = block_profile.get_attribute('href')

            user_urls = self.tag_search(ignore=name_profile)
            self.file_write('non_filtered/user_urls_commentators', user_urls)
            with open('data/User_urls_commentators.txt', 'r') as file:
                size = len(file.readlines())
                print(f'Количество собранных пользователей: {size}')

    # собирает список пабликов по тегу
    def hashtag_public_search(self, username, tag_search, search_depth=SearchUser.search_depth, ):
        """
        search_name - имя, которое будет вводиться в строку поиска по профилям
        delete_file - если "yes", то очистит файл со ссылками перед записью
        """
        browser = self.browser

        print(f'--- Сбор ссылок по запросу: {tag_search} ---')
        browser.get(f"https://www.instagram.com/{username}/")
        used_by_url = []

        search_input = self.search_element((By.CSS_SELECTOR, 'div.QY4Ed.P0xOK > input'))
        search_input.send_keys(tag_search)

        public_urls = self.tag_search(ignore=username, parameter=1.5)
        for i in range(search_depth):
            used_by_url.append(public_urls[i - 1])
        self.select_subscribers(username, used_by_url, filter_mode='on')

    # собирает пользователей "по конкуренту" со списка ссылок
    def select_subscribers(self, username, iter_count, url_public_list=None, filter_mode="off",
                           scroll_number_subscribers_list=SearchUser.scroll_number_subscribers_list,
                           ):
        browser = self.browser
        timeout_exception_count = 0
        if url_public_list is None:
            url_public_list = []
            self.file_read('url_lists/public_url_for_subscribe', url_public_list)
            print(f'===> Итерация сбора {iter_count+ 1} из {len(url_public_list)//10 + 1}. <===')
            url_public_list = url_public_list[int(str(iter_count) + '0'):int(str(iter_count + 1) + '0')]
        for url in url_public_list:
            try:
                browser.get(url)
                user_name = url.split("/")[-2]
                print(f'{datetime.now().strftime("%H:%M:%S")} Перешёл в профиль: {user_name}', end=' ======> ')

                if filter_mode == 'on':
                    self.should_be_compliance_with_limits(max_coefficient=SearchUser.coefficient_subscribers,
                                                          posts_max=SearchUser.posts_max,
                                                          posts_min=SearchUser.posts_min,
                                                          subscribers_max=SearchUser.subscribers_max,
                                                          subscribers_min=SearchUser.subscribers_min,
                                                          subscriptions_max=SearchUser.subscriptions_max,
                                                          subscriptions_min=SearchUser.subscriptions_min,
                                                          break_limit=SearchUser.break_limit)
                    self.should_be_stop_word_in_biography(data.stop_word_public_dict)

                subscribes_button = self.search_element((By.CSS_SELECTOR, 'li:nth-child(2) > a'))
                subscribes_button.click()

                subscribes_ul = self.search_element((By.CSS_SELECTOR, 'div.RnEpo.Yx5HN > div > div > div.isgrP'),
                                                    type_wait=ec.presence_of_element_located)
                for i in range(scroll_number_subscribers_list + 1):
                    browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", subscribes_ul)
                    self.search_element((By.CSS_SELECTOR, 'li div svg.By4nA'), timeout=10,
                                        type_wait=ec.invisibility_of_element_located)
                    time.sleep(0.5)
                    self.search_element((By.CSS_SELECTOR, 'li div svg.By4nA'), timeout=10,
                                        type_wait=ec.invisibility_of_element_located)
                    time.sleep(0.5)

                user_urls = self.tag_search(ignore=username)
                self.file_write('non_filtered/user_urls_subscribers', user_urls)
                with open('data/non_filtered/user_urls_subscribers.txt', 'r') as file:
                    size = len(file.readlines())
                    print(f'Успешно. Количество собранных пользователей: {size}.')
            except AssertionError as assertion:
                assertion = str(assertion.args)
                text = re.sub("[)(',]", '', assertion)
                print(text)
                continue
            except TimeoutException:
                timeout_exception_count += 1
                if timeout_exception_count == 3:
                    break
                print('  TimeoutException ---')
                continue

            except LoginError:
                print('= = = = = = = = Не получилось залогиниться. = = = = = = = =')
                continue

            except Exception:
                traceback_text = traceback.format_exc()
                date = datetime.now().strftime("%d-%m %H:%M:%S")
                self.file_write('logs/select', date, traceback_text)
