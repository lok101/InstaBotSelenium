from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

import data
from module.message_text_module import ErrorMessage, LoginErrorMessage, FilterMessage
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from module.exception_module import *
from selenium import webdriver
from datetime import datetime
from settings import *
from data import *
import traceback
import pickle
import random
import time
import json


class BaseClass:

    def __init__(self):

        self.link = 'https://www.instagram.com/'
        self.username = None
        self.password = None
        self.browser = None
        self.chrome_options = None
        self.read_file_path = None
        self.write_file_path = None

        self.headless = True
        self.proxy = True
        self.load_strategy = True

        self.mode = None
        self.accounts_key_mask = None
        self.accounts_key_number = None
        self.user_url = None

        self.exception = None
        self.exception_text = None

        self.min_timeout = None
        self.max_timeout = None
        self.count_limit = None
        self.cycle = None
        self.followers = None
        self.count_iteration = 0

    def browser_parameter_set(self):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--log-level=3')
        self.chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        if self.headless is True:
            self.chrome_options.add_argument("--headless")
        if self.proxy is True:
            self.chrome_options.add_argument(f'--proxy-server={proxy_list}')
        if self.load_strategy is True:
            self.chrome_options.page_load_strategy = 'eager'

    def parameter_input_and_set(self):
        user_input = input('Укажите режим работы (-параметры): ')

        if 'sub' in user_input.split(' ')[0]:
            self.set_mode_parameter('subscribe', 'main_account')

        elif 'uns' in user_input.split(' ')[0]:
            self.set_mode_parameter('unsubscribe', 'main_account')

        elif 'fil' in user_input.split(' ')[0]:
            self.set_mode_parameter('filter', 'bot_account')

        elif 'sel' in user_input.split(' ')[0]:
            self.set_mode_parameter('parse', 'bot_account')
            self.read_file_path = 'url_lists/subscribers_urls.txt'
            self.write_file_path = 'non_filtered/subscribers_urls.txt'
            with open(f'data/{self.write_file_path}', 'w'):
                print(f'Файл: "{self.write_file_path}" - очищен.')

        if '-p' in user_input:
            self.proxy = False
        if '-h' in user_input:
            self.headless = False
        if '-e' in user_input:
            self.load_strategy = False
        if '-bot' in user_input:
            self.accounts_key_mask = 'bot_account'
        if '-main' in user_input:
            self.accounts_key_mask = 'main_account'

    def accounts_input(self):

        account_list = []
        if self.accounts_key_mask == 'main_account':
            user_input = input('Введите имя аккаунта: ')
            account_list = user_input.split(' ')

        elif self.accounts_key_mask == 'bot_account':
            for key in data.user_dict:
                if 'bot_account' in key:
                    account_list.append(key.split('-')[1])
        else:
            raise BotException('Неизвестная маска аккаунта.')

        self.accounts_key_number = account_list

    def cookie_login(self):
        self.browser.delete_all_cookies()
        for cookie in pickle.load(open(f'data/cookies/{self.username}_cookies', 'rb')):
            self.browser.add_cookie(cookie)
        time.sleep(1)
        self.browser.refresh()
        self.should_be_verification_form()
        self.should_be_login_button()
        print('Залогинился через cookies.')

    def not_cookie_login(self):
        self.browser.get(self.link)

        username_input = self.search_element((By.NAME, "username"))
        username_input.clear()
        username_input.send_keys(self.username)

        password_input = self.search_element((By.NAME, "password"))
        password_input.clear()
        password_input.send_keys(self.password)

        password_input.send_keys(Keys.ENTER)
        time.sleep(5)
        self.should_be_login_form_error()
        self.should_be_verification_form()
        self.should_be_verification_email()
        self.should_be_phone_number_input()
        self.should_be_verification_phone_number()
        self.should_be_login_button()

        # сохраняем cookies
        pickle.dump(self.browser.get_cookies(), open(f'data/cookies/{self.username}_cookies', 'wb'))
        print(f'Залогинился и создал cookies ===> data/cookies/{self.username}_cookies.')

    def check_proxy_ip(self):
        self.browser.get("https://api.myip.com/")
        # noinspection PyTypeChecker
        pre = self.search_element((By.TAG_NAME, "body"), type_wait=ec.presence_of_element_located).text
        actual_ip = json.loads(pre)['ip']
        if actual_ip in my_ip:
            raise ConnectionError('При подключении через прокси зафиксирован "родной" IP-адрес.')
        date = datetime.now().strftime("%H:%M:%S")
        print(f'{date} Подключение через прокси: {actual_ip}', end=' ===> ')

    def get_link(self, locator):
        # noinspection PyTypeChecker
        item = self.search_element(locator, type_wait=ec.presence_of_element_located, timeout=10)
        url = item.get_attribute('src')
        return url

    def set_mode_parameter(self, parameter, mask):
        self.mode = parameter
        BotException.mode = parameter
        self.accounts_key_mask = mask

    # возвращает элемент с использованием явного ожидания
    def search_element(self, locator, timeout=StartSettings.web_driver_wait, type_wait=ec.element_to_be_clickable):
        return WebDriverWait(self.browser, timeout).until(type_wait(locator))

    # возвращает список по тегу
    def tag_search(self, parameter=1, ignore=None):
        """
        Parameter = 1 - возвращает список ссылок на профили
        parameter == 1.5 - возвращает список ссылок на профили в выпадающем меню поиска
        ignore - ключевое слово для игнорирования (сверяется со ссылкой)
        """
        list_urls = set()
        while True:
            try:
                if parameter == 1:
                    self.search_element((By.CSS_SELECTOR, 'div.Pkbci > button'))
                    tags = self.browser.find_elements(By.TAG_NAME, 'a')
                    for public_block in tags:
                        profile_url = public_block.get_attribute('href')
                        len_user_url = len(profile_url.split('/'))  # у ссылки на профиль равен пяти.
                        if len_user_url == 5 \
                                and 'www.instagram.com' in profile_url \
                                and self.username not in profile_url \
                                and 'explore' not in profile_url \
                                and ignore not in profile_url:
                            list_urls.add(profile_url)
                    return list_urls

                elif parameter == 1.5:
                    list_urls = []
                    self.search_element((By.CSS_SELECTOR, 'div > a.-qQT3'))
                    tags = self.browser.find_elements(By.TAG_NAME, 'a')
                    for public_block in tags:
                        profile_url = public_block.get_attribute('href')
                        len_user_url = len(profile_url.split('/'))  # у ссылки на профиль равен пяти.
                        if len_user_url == 5 \
                                and 'www.instagram.com' in profile_url \
                                and self.username not in profile_url \
                                and 'explore' not in profile_url \
                                and ignore not in profile_url:
                            list_urls.append(profile_url)
                    return list_urls

                elif parameter == 2:
                    time.sleep(5)
                    tags = self.browser.find_elements(By.TAG_NAME, 'a')
                    for post in tags:
                        post_url = post.get_attribute('href')
                        if '/p/' in post_url:
                            list_urls.add(post_url)
                    return list_urls

            except StaleElementReferenceException:
                print(StaleElementReferenceException)
                continue

    # возвращает список из 9 постов по хештегу
    def select_url_posts_to_hashtag(self, hashtag):
        self.browser.get(f'https://www.instagram.com/explore/tags/{hashtag}/')
        posts_block = self.search_element((By.XPATH, '//main/article/div[1]/div/div'))
        posts = posts_block.find_elements_by_tag_name('a')
        posts_url_list = []

        for post in posts:
            post_url = post.get_attribute('href')
            if '/p/' in post_url:
                posts_url_list.append(post_url)
        print('Ссылки на посты собраны.')
        return posts_url_list

    @staticmethod
    def file_read(file_name, value, operating_mode='r'):
        with open(f'data/{file_name}', operating_mode, encoding='utf-8') as file:
            if isinstance(value, set):
                for link in file:
                    value.add(link)
            elif isinstance(value, list):
                for link in file:
                    value.append(link)

    @staticmethod
    def file_write(file_name, value, value2=None, operating_mode='a'):
        with open(f'data/{file_name}', operating_mode, encoding='utf-8') as file:
            if value2 is not None:
                file.write(str(value) + '\n')
                file.write(str(value2) + '\n \n')
            elif isinstance(value, (list, set)):
                if '\n' in value.pop():
                    for item in value:
                        file.write(item)
                else:
                    for item in value:
                        file.write(item + '\n')
            else:
                if '\n' in value:
                    file.write(str(value))
                else:
                    file.write(str(value) + '\n')

    # сохраняет лог исключения в файл и печатает сообщение об исключении в консоль
    def standard_exception_handling(self):

        self.save_log_exception()
        exception_name = str(type(self.exception)).split("'")[1].split('.')[-1]
        if self.mode == 'filtered':
            raise BotFinishTask(FilterMessage.list_empty)
        print(f'\nЛог: {self.mode}/{exception_name} -- {self.exception}')

    def catching_critical_bot_exceptions(self):

        if isinstance(self.exception, (VerificationError, LoginError)):
            exception_name = str(type(self.exception)).split("'")[1].split('.')[-1]
            path = f'logs/{exception_name}.txt'
            self.file_write(path, self.username, self.exception)

        elif isinstance(self.exception, ActivBlocking):
            pass

        print(f'{self.exception}')

    def catching_non_critical_bot_exceptions(self):

        if isinstance(self.exception, UserPageNotExist):
            self.file_write('ignore_list.txt', self.user_url)

        elif isinstance(self.exception, (PageLoadingError, PageNotAvailable)):
            pass

        print(f'{self.exception}')

    def bot_filter_out_handling(self):

        if not isinstance(self.exception, EmptyProfile):
            exception_name = str(type(self.exception)).split("'")[1].split('.')[-1]
            path = f'logs/filtered/filter_out/{exception_name}.txt'
            message = str(self.user_url.split("\n")[0]) + ' ----- ' + str(self.exception)
            self.file_write(path, message)

        self.file_write('ignore_list.txt', self.user_url)
        print(f'{self.exception}')

    def save_log_exception(self):
        exception_name = str(type(self.exception)).split("'")[1].split('.')[-1]
        date = datetime.now().strftime("%d-%m %H:%M:%S")
        path = f'logs/{self.mode}/{exception_name}.txt'
        exception_text = traceback.format_exc()
        self.file_write(path, date, exception_text)

        if 'CONNECTION_FAILED' in exception_text:
            timeout = StartSettings.err_proxy_timeout
            error_name = exception_text.split('net::')[1].split('\n')[0]
            print(f'{date.split(" ")[1]} -- {self.mode} >> {error_name}. ',
                  f'Запись добавлена в лог. Таймаут {timeout} секунд.')
            time.sleep(timeout)
            if self.mode == 'authorize':
                raise ConnectionError

    def test_log(self):
        self.mode = 'test'
        try:
            print('Exception ===> ', end='')
            raise Exception('Тестовый запуск.')
        except Exception as exception:
            self.exception = exception
            self.standard_exception_handling()
            try:
                print('BotCriticalException ===> ', end='')
                raise BotCriticalException('Тестовый запуск.')
            except BotCriticalException as exception:
                self.exception = exception
                self.catching_critical_bot_exceptions()
                try:
                    print('BotNotCriticalException ===> ', end='')
                    raise BotNonCriticalException('Тестовый запуск.')
                except BotNonCriticalException as exception:
                    self.exception = exception
                    self.bot_not_critical_exception_handling()
                    try:
                        print('FilterException ===> ', end='')
                        raise EmptyProfile('Тестовый запуск.')
                    except EmptyProfile as exception:
                        self.exception = exception
                        self.bot_filter_exception_handling()
                        try:
                            print('BotFinishTask ===> ', end='')
                            raise BotFinishTask('Тестовый запуск.')
                        except BotFinishTask as exception:
                            self.exception = exception
                            self.bot_final_task_exception_handling()
                            self.browser.quit()

    # возвращает количество постов, подписчиков, подписок и коэффициент подписки/подписчики
    def return_number_posts_subscribe_and_subscribers(self):
        dict_return = dict()
        try:
            # noinspection PyTypeChecker
            subscriptions_field = self.search_element((By.CSS_SELECTOR, 'li:nth-child(3) > a > div > span.g47SY'),
                                                      type_wait=ec.presence_of_element_located, timeout=3)

            dict_return['subs'] = int(
                subscriptions_field.text.replace(" ", "").replace(',', ''))
        except TimeoutException:
            dict_return['subs'] = 0

        try:
            # noinspection PyTypeChecker
            subscribe_field = self.search_element((By.CSS_SELECTOR, 'li:nth-child(2) > a > div > span.g47SY'),
                                                  type_wait=ec.presence_of_element_located, timeout=3)
            if ',' in subscribe_field.text:
                dict_return['follow'] = int(
                    subscribe_field.text.replace(" ", "").replace(',', '').replace('тыс.', '00').replace('млн',
                                                                                                         '00000'))
            else:
                dict_return['follow'] = int(
                    subscribe_field.text.replace(" ", "").replace('тыс.', '000').replace('млн', '000000'))
        except TimeoutException:
            dict_return['follow'] = 1

        # noinspection PyTypeChecker
        post_number_field = self.search_element((By.CSS_SELECTOR, 'li:nth-child(1) > div > span.g47SY'),
                                                type_wait=ec.presence_of_element_located)
        dict_return['posts'] = int(
            post_number_field.text.replace(" ", "").replace(',', '').replace('тыс.', '000').replace('млн', '000000'))

        return dict_return

    # возвращает результат вычитания второго и третьего множества из первого
    def difference_sets(self, item1, item2, item3=None):
        user_set1, user_set2, user_set3 = set(), set(), set()
        if item3 is not None:
            if isinstance(item1, str):
                self.file_read(item1, user_set1)
                self.file_read(item2, user_set2)
                self.file_read(item3, user_set3)
                final_set = user_set1.difference(user_set2, user_set3)
            elif isinstance(item1, set):
                self.file_read(item2, user_set2)
                self.file_read(item3, user_set3)
                final_set = item1.difference(user_set2, user_set3)
        else:
            if isinstance(item1, str):
                self.file_read(item1, user_set1)
                self.file_read(item2, user_set2)
                final_set = user_set1.difference(user_set2)
            elif isinstance(item1, set):
                self.file_read(item2, user_set2)
                final_set = item1.difference(user_set2)
        return final_set

    # ищет и нажимает кнопку "подписаться"
    def press_to_button_subscribe(self):
        button = self.search_element((By.XPATH, '//button'))
        if 'подписаться' in button.text.lower():
            iteration_limit = 10
            iteration_count = 0
            while iteration_count < iteration_limit:
                iteration_count += 1
                button.click()
                time.sleep(random.randrange(self.min_timeout, self.max_timeout))
                self.should_be_subscribe_and_unsubscribe_blocking()
                if self.mode != 'short_subscribe':
                    self.file_write('ignore_list.txt', self.user_url)
                self.count_iteration += 1
                print('Успешно подписался.')
                break
        else:
            print('Кнопка не найдена.')
            self.file_write('ignore_list.txt', self.user_url)
            time.sleep(random.randrange(Subscribe.min_timeout, Subscribe.max_timeout))

    # переходит на страницу по ссылке, запускает проверки на наличие страницы, загрузку страницы и наличие микробана
    def go_to_user_page(self, end_str=' ===> '):
        self.browser.get(self.user_url)
        username = self.user_url.split("/")[-2]
        print(
            f'{datetime.now().strftime("%H:%M:%S")} - {self.username} - ',
            f'[{self.count_iteration + 1}/{self.count_limit}]',
            f'Перешёл в профиль: {username}', end=end_str)

        self.should_be_instagram_page()
        self.should_be_activity_blocking()
        self.should_be_user_page()
        self.should_be_verification_form()

    # переходит на свою страницу, запускает проверки, кладёт количество подписок в переменную
    def go_to_my_profile_page(self, end_str='\n'):
        url = f'https://www.instagram.com/{self.username}/'
        self.browser.get(url)
        self.should_be_instagram_page()
        self.should_be_activity_blocking()
        self.should_be_verification_form()

        self.followers = self.return_number_posts_subscribe_and_subscribers()['subs']
        print(f"Количество подписок: {self.followers}", end=end_str)

    # проверяет наличие окна "добавьте номер телефона"
    def should_be_phone_number_input(self):
        try:
            # noinspection PyTypeChecker
            self.search_element((By.CSS_SELECTOR, 'div.qF0y9.Igw0E.IwRSH.eGOV_._4EzTm.dQ9Hi > h3'), timeout=1,
                                type_wait=ec.presence_of_element_located)
            raise VerificationError(LoginErrorMessage.input_phone_number)

        except TimeoutException:
            pass

    # проверяет наличие окна "подтвердите номер телефона"
    def should_be_verification_phone_number(self):
        try:
            # noinspection PyTypeChecker
            self.search_element((By.XPATH, '/html/body/div[1]/section/main/div[2]/div/div/div/div[1]/div[1]/span'),
                                timeout=1, type_wait=ec.presence_of_element_located)
            raise VerificationError(LoginErrorMessage.input_code_from_sms)

        except TimeoutException:
            pass

    # проверяет наличие запроса на верификацию
    def should_be_verification_form(self):
        try:
            # noinspection PyTypeChecker
            self.search_element((By.CSS_SELECTOR, 'div.ctQZg.KtFt3 > button > div'), timeout=2)
            raise VerificationError(LoginErrorMessage.verification_form)

        except TimeoutException:
            pass

    # проверяет наличие окна "подтвердите почту"
    def should_be_verification_email(self):
        try:
            # noinspection PyTypeChecker
            self.search_element((By.CSS_SELECTOR, 'div > div.GNbi9 > div > p'),
                                timeout=1, type_wait=ec.presence_of_element_located)
            raise VerificationError(LoginErrorMessage.verification_email)
        except TimeoutException:
            pass

    # проверяет наличие ошибки "Не получилось залогиниться" (красный шрифт под формой авторизации).
    def should_be_login_form_error(self):
        try:
            # noinspection PyTypeChecker
            element = self.search_element((By.CSS_SELECTOR, '#slfErrorAlert'),
                                          timeout=1, type_wait=ec.presence_of_element_located)
            if 'К сожалению, вы ввели неправильный пароль.' in element.text:
                raise LoginError(LoginErrorMessage.error_pass)
            raise LoginError(LoginErrorMessage.login_form_error)
        except TimeoutException:
            pass

    # проверяет, если ли мини-иконка домика вверху страницы (используется для проверки входа в аккаунт)
    def should_be_login_button(self):
        try:
            # noinspection PyTypeChecker
            self.search_element((By.CSS_SELECTOR, 'div.ctQZg.KtFt3 > div > div:nth-child(1)'), timeout=2,
                                type_wait=ec.presence_of_element_located)

        except TimeoutException:
            raise LoginError(LoginErrorMessage.not_login)

    # проверяет наличие "микробана" на подписку/отписку
    def should_be_subscribe_and_unsubscribe_blocking(self):
        try:
            # noinspection PyTypeChecker
            self.search_element((By.CSS_SELECTOR, 'div._08v79 > h3'), timeout=2,
                                type_wait=ec.presence_of_element_located)
            raise ActivBlocking(ErrorMessage.subscribe_unsubscribe_blocking)

        except TimeoutException:
            pass

    # проверяет наличие "микробана" на активность
    def should_be_activity_blocking(self):
        try:
            # noinspection PyTypeChecker
            error_message = self.search_element((By.CSS_SELECTOR, 'div > div.error-container > p'), timeout=2,
                                                type_wait=ec.presence_of_element_located)
            if 'Подождите несколько минут, прежде чем пытаться снова' in error_message.text:
                raise ActivBlocking(ErrorMessage.activiti_blocking)
            else:
                print('Неизвестное всплывающее окно при вызове "should_be_activity_blocking".')
        except TimeoutException:
            pass

    # проверяет, существует ли страница по данной ссылке
    def should_be_user_page(self):
        while True:
            try:
                # noinspection PyTypeChecker
                error_message = self.search_element((By.CSS_SELECTOR, 'div > div > h2'), timeout=1,
                                                    type_wait=ec.presence_of_element_located)
                if 'К сожалению, эта страница недоступна' in error_message.text:
                    raise UserPageNotExist(ErrorMessage.page_not_exist)
                elif 'Это закрытый аккаунт' in error_message.text:
                    raise PageNotAvailable(FilterMessage.profile_closed)
                elif 'Вам исполнилось' in error_message.text:
                    raise PageNotAvailable(ErrorMessage.check_age)
                else:
                    print('Неизвестное окно при вызове "should_be_user_page".')
                break

            except TimeoutException:
                break

            except StaleElementReferenceException:
                continue

    # проверяет, находится ли на странице инстаграм (ищет логотип слева-сверху)
    def should_be_instagram_page(self):
        try:
            # noinspection PyTypeChecker
            self.search_element((By.CSS_SELECTOR, '[href=\'/\']'), timeout=15,
                                type_wait=ec.presence_of_element_located)

        except TimeoutException:
            raise PageLoadingError(ErrorMessage.page_loading_error)

    # проверяет, находится ли на странице логина
    def should_be_home_page(self):
        try:
            # noinspection PyTypeChecker
            self.search_element((By.NAME, "username"),
                                timeout=10, type_wait=ec.presence_of_element_located)
            print(f'Логин с аккаунта - {self.username}')
        except TimeoutException:
            raise LoginError(LoginErrorMessage.not_login_page)
