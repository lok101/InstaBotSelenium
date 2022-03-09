from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from module.message_text_module import InformationMessage, LoginErrorMessage, FilterMessage
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from module.exception_module import *
from module.option import BotOption
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
        self.account_option = BotOption()
        self.browser = None

        self.user_url = None
        self.count_limit = None
        self.cycle = None
        self.subscribes = None
        self.count_iteration = 0
        self.count = 0

    def cookie_login(self):
        self.browser.delete_all_cookies()
        for cookie in pickle.load(open(f'data/cookies/{self.account_option.username}_cookies', 'rb')):
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
        username_input.send_keys(self.account_option.username)

        password_input = self.search_element((By.NAME, "password"))
        password_input.clear()
        password_input.send_keys(self.account_option.password)

        password_input.send_keys(Keys.ENTER)
        time.sleep(5)
        self.should_be_login_form_error()
        self.should_be_verification_form()
        self.should_be_verification_email()
        self.should_be_phone_number_input()
        self.should_be_verification_phone_number()
        self.should_be_login_button()

        # сохраняем cookies
        pickle.dump(self.browser.get_cookies(), open(f'data/cookies/{self.account_option.username}_cookies', 'wb'))
        print(f'Залогинился и создал cookies ===> data/cookies/{self.account_option.username}_cookies.')

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

    # возвращает элемент с использованием явного ожидания
    def search_element(self, locator, timeout=StartSettings.web_driver_wait, type_wait=ec.element_to_be_clickable):
        return WebDriverWait(self.browser, timeout).until(type_wait(locator))

    # возвращает список по тегу
    def tag_search(self, ignore=None):
        list_urls = set()
        while True:
            try:
                self.search_element((By.CSS_SELECTOR, 'div.Pkbci > button'))
                tags = self.browser.find_elements(By.TAG_NAME, 'a')
                for public_block in tags:
                    profile_url = public_block.get_attribute('href')
                    len_user_url = len(profile_url.split('/'))  # у ссылки на профиль равен пяти.
                    if len_user_url == 5 \
                            and 'www.instagram.com' in profile_url \
                            and self.account_option.username not in profile_url \
                            and 'explore' not in profile_url \
                            and ignore not in profile_url:
                        list_urls.add(profile_url)
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
        exception_name = str(type(self.account_option.exception)).split("'")[1].split('.')[-1]
        if BotException.mode == data.parameters['fil'] and isinstance(self.account_option.exception, KeyError):
            raise BotFinishTask(FilterMessage.list_empty)
        print(f'\nЛог: {BotException.mode}/{exception_name} -- {self.account_option.exception}')

    def catching_critical_bot_exceptions(self):

        if isinstance(self.account_option.exception, (VerificationError, LoginError)):
            exception_name = str(type(self.account_option.exception)).split("'")[1].split('.')[-1]
            path = f'logs/{exception_name}.txt'
            message = self.account_option.username.split("\n")[0] + ' ----- ' + str(self.account_option.exception)
            self.file_write(path, message)

        elif isinstance(self.account_option.exception, ActivBlocking):
            pass

        print(f'{self.account_option.exception}')

    def catching_non_critical_bot_exceptions(self):

        if isinstance(self.account_option.exception, UserPageNotExist):
            self.file_write('ignore_list.txt', self.user_url)

        elif isinstance(self.account_option.exception, (PageLoadingError, PageNotAvailable)):
            pass

        print(f'{self.account_option.exception}')

    def bot_filter_out_handling(self):

        if not isinstance(self.account_option.exception, EmptyProfile):
            exception_name = str(type(self.account_option.exception)).split("'")[1].split('.')[-1]
            path = f'logs/{data.parameters["fil"]}/filter_out/{exception_name}.txt'
            message = str(self.user_url.split("\n")[0]) + ' ----- ' + str(self.account_option.exception)
            self.file_write(path, message)

        self.file_write('ignore_list.txt', self.user_url)
        print(f'{self.account_option.exception}')

    def save_log_exception(self):
        exception_name = str(type(self.account_option.exception)).split("'")[1].split('.')[-1]
        date = datetime.now().strftime("%d-%m %H:%M:%S")
        path = f'logs/{BotException.mode}/{exception_name}.txt'
        exception_text = traceback.format_exc()
        self.file_write(path, date, exception_text)

        if 'CONNECTION_FAILED' in exception_text:
            timeout = StartSettings.err_proxy_timeout
            error_name = exception_text.split('net::')[1].split('\n')[0]
            print(f'{date.split(" ")[1]} -- {BotException.mode} >> {error_name}. ',
                  f'Запись добавлена в лог. Таймаут {timeout} секунд.')
            time.sleep(timeout)

    # прокручивает список, возвращает элементы списка
    def scrolling_div_block_and_return_list_of_users(self, locator, count=5):
        scroll_block = self.search_element(locator, type_wait=ec.presence_of_element_located)
        following_users = []

        if self.account_option.mode == data.parameters['uns']:
            while self.subscribes - 30 > len(following_users):
                following_users = self.one_scroll_block_and_return_list_of_users(scroll_block)
                print(f'Загрузил подписок - [{len(following_users)}/{self.subscribes}]')

        elif self.account_option.mode == data.parameters['par']:
            for i in range(count):
                self.one_scroll_block_and_return_list_of_users(scroll_block)

        else:
            raise BotCriticalException(
                'Неизвестный режим работы при вызове метода "scrolling_div_block_and_return_list_of_users".')

        return following_users

    def one_scroll_block_and_return_list_of_users(self, scroll_block):
        self.browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_block)
        self.search_element((By.CSS_SELECTOR, 'li div svg.By4nA'), timeout=10,
                            type_wait=ec.invisibility_of_element_located)
        time.sleep(0.5)
        self.search_element((By.CSS_SELECTOR, 'li div svg.By4nA'), timeout=10,
                            type_wait=ec.invisibility_of_element_located)
        time.sleep(0.5)
        following_div_block = self.search_element((By.CSS_SELECTOR, 'div > div > div.isgrP > ul > div'))

        return following_div_block.find_elements(By.TAG_NAME, "li")

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

    def set_user_url_from_file(self, file_path, ignore_list_path, ignore_list_2_path=None):
        if ignore_list_2_path is not None:
            user_list = self.difference_sets(file_path, ignore_list_path, ignore_list_2_path)
        else:
            user_list = self.difference_sets(file_path, ignore_list_path)
        self.user_url = user_list.pop()
        self.file_write(file_path, user_list, operating_mode='w')

    def get_statistics_on_filtration(self):
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
            f'Отобрано в сессии - {self.count}.\n')

    # ищет и нажимает кнопку "подписаться"
    def press_to_subscribe_button(self):
        button = self.search_element((By.XPATH, '//button'))
        if 'подписаться' in button.text.lower():
            iteration_limit = 10
            iteration_count = 0
            while iteration_count < iteration_limit:
                iteration_count += 1
                button.click()
                time.sleep(random.randrange(Subscribe.min_timeout, Subscribe.max_timeout))
                self.should_be_subscribe_and_unsubscribe_blocking()
                self.file_write('ignore_list.txt', self.user_url)
                self.count_iteration += 1
                print('Успешно подписался.')
                break
        else:
            print('Кнопка не найдена.')
            self.file_write('ignore_list.txt', self.user_url)
            time.sleep(random.randrange(Subscribe.min_timeout, Subscribe.max_timeout))

    def check_limits_from_subscribe(self):
        if self.count_iteration % Subscribe.subscribe_in_session == 0 and self.count_iteration != 0:
            self.go_to_my_profile_page_and_set_subscribes_amount(end_str=' ')
            print(f'{datetime.now().strftime("%H:%M:%S")} Подписался на очередные',
                  f'{Subscribe.subscribe_in_session} пользователей. ',
                  f'Таймаут {Subscribe.sleep_between_iterations} минут.')

            user_list = self.difference_sets('filtered/user_urls_subscribers.txt', 'ignore_list.txt')
            print(f'= = = = Осталось профилей для подписки - {len(user_list)} = = = =')
            time.sleep(Subscribe.sleep_between_iterations * 60)

    def press_to_unsubscribe_button_and_set_timeouts(self, user):
        user.find_element(By.TAG_NAME, "button").click()  # нажать кнопку отписки
        time.sleep(random.randrange(Unsubscribe.min_sleep, Unsubscribe.max_sleep))
        self.search_element((By.CSS_SELECTOR, "button.-Cab_")).click()  # нажать кнопку подтверждения
        self.should_be_subscribe_and_unsubscribe_blocking()
        self.count_iteration += 1
        print(
            f'{datetime.now().strftime("%H:%M:%S")} - {self.account_option.username} - ',
            f'[{self.count_iteration}/10] - Успешно отписался.')

    # переходит на страницу по ссылке, запускает проверки на наличие страницы, загрузку страницы и наличие микробана
    def go_to_user_page(self, end_str=' ===> '):
        self.browser.get(self.user_url)
        username = self.user_url.split("/")[-2]
        print(
            f'{datetime.now().strftime("%H:%M:%S")} - {self.account_option.username} - ',
            f'[{self.count_iteration + 1}/{self.count_limit}]',
            f'Перешёл в профиль: {username}', end=end_str)

        self.should_be_instagram_page()
        self.should_be_activity_blocking()
        self.should_be_user_page()
        self.should_be_verification_form()

    # переходит на свою страницу, запускает проверки, кладёт количество подписок в переменную
    def go_to_my_profile_page_and_set_subscribes_amount(self, end_str='\n'):
        url = f'https://www.instagram.com/{self.account_option.username}/'
        self.browser.get(url)
        self.should_be_instagram_page()
        self.should_be_activity_blocking()
        self.should_be_verification_form()

        self.subscribes = self.return_number_posts_subscribe_and_subscribers()['subs']
        print(f"Количество подписок: {self.subscribes}", end=end_str)

    # проверяет наличие запроса на верификацию
    def should_be_verification_form(self):
        try:
            # noinspection PyTypeChecker
            self.search_element((By.CSS_SELECTOR, 'div.ctQZg.KtFt3 > button > div'), timeout=2)
            raise VerificationError(LoginErrorMessage.verification_form)

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
            raise ActivBlocking(InformationMessage.subscribe_unsubscribe_blocking)

        except TimeoutException:
            pass

    # проверяет наличие "микробана" на активность
    def should_be_activity_blocking(self):
        try:
            # noinspection PyTypeChecker
            error_message = self.search_element((By.CSS_SELECTOR, 'div > div.error-container > p'), timeout=2,
                                                type_wait=ec.presence_of_element_located)
            if 'Подождите несколько минут, прежде чем пытаться снова' in error_message.text:
                raise ActivBlocking(InformationMessage.activiti_blocking)
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
                    raise UserPageNotExist(InformationMessage.page_not_exist)
                elif 'Это закрытый аккаунт' in error_message.text:
                    raise PageNotAvailable(FilterMessage.profile_closed)
                elif 'Вам исполнилось' in error_message.text:
                    raise PageNotAvailable(InformationMessage.check_age)
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
            raise PageLoadingError(InformationMessage.page_loading_error)

    # проверяет, находится ли на странице логина
    def should_be_home_page(self):
        try:
            # noinspection PyTypeChecker
            self.search_element((By.NAME, "username"),
                                timeout=10, type_wait=ec.presence_of_element_located)
            print(f'Логин с аккаунта - {self.account_option.username}')
        except TimeoutException:
            raise LoginError(LoginErrorMessage.not_login_page)
