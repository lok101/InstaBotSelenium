from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as ec

from datetime import datetime
import random

from module import exception, message_text, selectors
from settings import Subscribe, StartSettings
from module import data_base

from module.base_module import BaseClass


class Check:
    @staticmethod
    def should_be_user_page(bot):
        while True:
            try:
                error_message = BaseClass.search_element(
                    bot, selectors.Technical.header_on_page_close,
                    type_wait=ec.presence_of_element_located, timeout=1)
                if 'К сожалению, эта страница недоступна' in error_message.text:
                    raise exception.UserPageNotExist(
                        bot, message_text.InformationMessage.page_not_exist)
                elif 'Это закрытый аккаунт' in error_message.text:
                    raise exception.PageNotAvailable(
                        bot, message_text.FilterMessage.profile_closed)
                elif 'Вам исполнилось' in error_message.text:
                    raise exception.PageNotAvailable(
                        bot, message_text.InformationMessage.check_age)
                else:
                    print('Неизвестное окно при вызове "should_be_user_page".')
                break

            except TimeoutException:
                break

            except StaleElementReferenceException:
                continue

    @staticmethod
    def should_be_login_page(bot):
        try:
            BaseClass.search_element(bot, selectors.Login.username, timeout=10,
                                     type_wait=ec.presence_of_element_located)
            Print.to_console(
                Text(bot).current_time(),
                Text(bot).account_name(),
                Text(bot).start_login(),
            )
        except TimeoutException:
            raise exception.LoginError(
                bot, message_text.LoginErrorMessage.not_login_page)

    @staticmethod
    def should_be_verification_forms(bot):
        Check.search_verification_for_email_form(bot)
        Check.search_any_verification_form(bot)

    @staticmethod
    def search_verification_for_email_form(bot):
        try:
            BaseClass.search_element(bot, selectors.Technical.red_label_danger_login, timeout=2)
            raise exception.VerificationError(
                bot, message_text.LoginErrorMessage.verification_email_form)

        except TimeoutException:
            pass

    @staticmethod
    def search_any_verification_form(bot):
        try:
            BaseClass.search_element(bot, selectors.Technical.verification_form, timeout=2)
            raise exception.CriticalVerificationError(
                bot, message_text.LoginErrorMessage.verification_form)

        except TimeoutException:
            pass

    @staticmethod
    def should_be_login_form_error(bot):
        try:
            element = BaseClass.search_element(
                bot, selectors.Login.label_about_error_under_login_button,
                timeout=10,
                type_wait=ec.presence_of_element_located)
            if 'К сожалению, вы ввели неправильный пароль.' in element.text:
                raise exception.LoginError(
                    bot, message_text.LoginErrorMessage.error_pass)
            if 'не принадлежит аккаунту' in element.text:
                raise exception.LoginError(
                    bot, message_text.LoginErrorMessage.error_account_name)
            raise exception.LoginError(
                bot, message_text.LoginErrorMessage.login_form_error)
        except TimeoutException:
            pass

    @staticmethod
    def should_be_login_button(bot, mode='login-pass'):
        try:
            BaseClass.search_element(bot, selectors.UserPage.home_button,
                                     timeout=10,
                                     type_wait=ec.presence_of_element_located)

        except TimeoutException:
            if mode == 'cookie':
                message = message_text.LoginErrorMessage.broke_cookie
            else:
                message = message_text.LoginErrorMessage.not_login
            raise exception.LoginError(bot, message)

    @staticmethod
    def should_be_subscribe_and_unsubscribe_blocking(bot):
        try:
            BaseClass.search_element(
                bot, selectors.Technical.alert_window_activity_blocking,
                type_wait=ec.presence_of_element_located, timeout=2)
            raise exception.ActivBlocking(
                bot, message_text.InformationMessage.subscribe_unsubscribe_blocking)

        except TimeoutException:
            pass

    @staticmethod
    def should_be_activity_blocking(bot):
        try:
            error_message = BaseClass.search_element(
                bot, selectors.Technical.header_on_stop_page,
                type_wait=ec.presence_of_element_located, timeout=2)
            if 'Подождите несколько минут, прежде чем пытаться снова' in error_message.text:
                raise exception.ActivBlocking(
                    bot, message_text.InformationMessage.activiti_blocking)
            elif 'cookie' in error_message.text:
                BaseClass.cookie_accept(bot)
            else:
                print('Неизвестное всплывающее окно при вызове "should_be_activity_blocking".')
        except TimeoutException:
            pass

    @staticmethod
    def should_be_instagram_page(bot):
        try:
            BaseClass.search_element(
                bot, selectors.UserPage.instagram_logo,
                type_wait=ec.presence_of_element_located, timeout=15)
        except TimeoutException:
            raise exception.PageLoadingError(
                bot, message_text.InformationMessage.page_loading_error)

    @staticmethod
    def check_cookie_accept_window(bot):
        try:
            BaseClass.search_element(
                bot, selectors.Technical.cookie_accept_window,
                type_wait=ec.presence_of_element_located, timeout=2)

            accept_button = BaseClass.search_element(
                bot, selectors.Technical.cookie_accept_window,
                type_wait=ec.presence_of_element_located)
            accept_button.click()
            Print.to_console(
                Text(bot).cookie_accept()
            )

        except TimeoutException:
            pass

    @staticmethod
    def check_proxy_ip(bot):
        bot.browser.get('https://api.myip.com/')
        BaseClass.compare_my_ip_and_base_ip(bot)
        Print.to_console(
            Text(bot).current_time(),
            Text(bot).account_name(),
            Text(bot).proxy_successful_connection()
        )


class Print:
    @staticmethod
    def to_console(*args):
        def inner(bot):
            for function in args:
                function(bot)

        return inner


class Text:
    def __init__(self, bot):
        self.bot = bot

    def account_name(self):
        print(f'{self.bot.account_data["user_name"]} - ', end='')

    def print_statistics_on_filtration(self):
        non_filtered, filtered = set(), set()
        Tools.get_user_url_from_file(self.bot,
                                     (BaseClass.parameters["non_filtered_path"]))  # вычитает из файла игнор лист
        Tools.file_read((BaseClass.parameters["non_filtered_path"]), non_filtered)
        Tools.file_read((BaseClass.parameters["filtered_path"]), filtered)
        print(
            f'\nНе отфильтровано - {len(non_filtered)}.'
            f'\nГотовых - {len(filtered)}.',
            f'\nОтобрано в сессии - [{self.bot.count}/{self.bot.cycle * 50}].\n')
        self.bot.cycle += 1

    def print_statistics_on_parce(self):
        non_filtered = set()
        Tools.file_read((BaseClass.parameters["non_filtered_path"]), non_filtered)
        self.bot.count_iteration += 1
        print(f'Успешно. В списке: {len(non_filtered)}.')

    def profile_page_info(self):
        username = self.bot.account_data['account_url'].split("/")[-2]
        print(f'[{self.bot.count_iteration + 1}/{self.bot.count_limit}] Перешёл в профиль: {username}', end=' ===> ')

    def unsubscribe_click_info(self):
        print(f'[{self.bot.count_iteration}/10] - Успешно отписался.')

    def subscribe_amount(self):
        print(f'Количество подписок в текущем профиле: {self.bot.subscribes}')

    def connection_failed(self):
        timeout = StartSettings.err_proxy_timeout
        print(
            f'{self.bot.account_data["WORK_MODE"]} >> '
            f'CONNECTION_FAILED. Запись добавлена в лог. Таймаут {timeout} секунд.'
        )

    def exception_info(self):
        exception_name = str(type(self.bot.account_data['exception'])).split("'")[1].split('.')[-1]
        print(f'\nИсключение обработано и добавлено в лог: {self.bot.account_data["WORK_MODE"]}/{exception_name}')

    def login_not_cookie(self):
        print(f'Залогинился и создал cookie-файл ===> '
              f'data/cookies/{self.bot.account_data["user_name"]}_cookies.')

    def print_timer(self):
        print(f'Установлен таймер {self.bot.account_data["timer"]} минут.')

    @staticmethod
    def subscribe_limit_info():
        print(f'Подписался на очередные {Subscribe.subscribe_in_session} пользователей. ',
              f'Таймаут {Subscribe.sleep_between_iterations} минут.')

    @staticmethod
    def proxy_successful_connection():
        date = datetime.now().strftime("%H:%M:%S")
        print(f'{date} Успешно подключился через прокси.', end=' ===> ')

    @staticmethod
    def login_from_cookie():
        print('Залогинился через cookie-файл.')

    @staticmethod
    def start_login():
        print(f'Попытка логина.')

    @staticmethod
    def subscribe_successful():
        print('Успешно подписался.')

    @staticmethod
    def button_not_found():
        print('Кнопка не найдена.')

    @staticmethod
    def current_time():
        print(f'{datetime.now().strftime("%H:%M:%S")} - ', end='')

    @staticmethod
    def shuffle_parce_file():
        print(f'Файл {BaseClass.parameters["parce_url_path"]} - перемешан.')

    @staticmethod
    def shuffle_filter_file():
        print(f'Файл {BaseClass.parameters["non_filtered_path"]} - перемешан.')

    @staticmethod
    def cookie_accept():
        print('Приняты настройки cookie. ')


class Tools:
    @staticmethod
    def difference_sets(file_path):
        account_list, ignore_list = set(), set()
        Tools.file_read(file_path, account_list)
        Tools.file_read(BaseClass.parameters['ignore_list_path'], ignore_list)
        account_list = account_list.difference(ignore_list)
        return account_list

    @staticmethod
    def file_read(file_path, value, operating_mode='r'):
        with open(f'data/{file_path}', operating_mode, encoding='utf-8') as file:
            if isinstance(value, set):
                for link in file:
                    value.add(link)
            elif isinstance(value, list):
                for link in file:
                    value.append(link)

    @staticmethod
    def file_write(file_path, value, operating_mode='a'):
        with open(f'data/{file_path}', operating_mode, encoding='utf-8') as file:
            if isinstance(value, (list, set)):
                for item in value:
                    if '\n' in item:
                        file.write(item)
                    else:
                        file.write(item + '\n')
            else:
                if '\n' in value:
                    file.write(str(value))
                else:
                    file.write(str(value) + '\n')

    @staticmethod
    def shaffle_file(file_path):
        file = []
        Tools.file_read(file_path, file)
        before = len(file)
        random.shuffle(file)
        Tools.file_write(file_path, file, operating_mode='w')
        file = []
        Tools.file_read(file_path, file)
        after = len(file)
        if before > after:
            raise Exception('Метод "shaffle_file" вернул меньше строк, чем получил.')
        elif before < after:
            raise Exception('Метод "shaffle_file" вернул больше строк, чем получил.')

    @staticmethod
    def add_accounts_to_data_base():
        accounts_list = list()
        Tools.file_read('accounts', accounts_list)
        for entry in accounts_list:
            user_name, user_pass, email_name, email_pass, email_codeword = entry.split(':')
            data_base.create_entry_db(user_name, user_pass, email_name, email_pass, email_codeword)

    @staticmethod
    def get_user_url_from_file(bot, file_path, difference_ignore_list=True):
        try:
            if difference_ignore_list:
                user_list = Tools.difference_sets(file_path)
            else:
                user_list = []
                Tools.file_read(file_path, user_list)
            bot.account_data['account_url'] = user_list.pop()
            Tools.file_write(file_path, user_list, operating_mode='w')
        except IndexError:
            raise exception.BotFinishTask(
                bot, message_text.InformationMessage.task_finish)
