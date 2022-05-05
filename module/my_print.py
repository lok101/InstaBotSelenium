from datetime import datetime
from module import base_module
from module.option import BotOption
from module.tools import Tools
from settings import Subscribe


class Print(base_module.BaseClass):
    def print_to_console_current_time_and_account_name(self, function):
        def inner():
            print(f'{datetime.now().strftime("%H:%M:%S")} - {self.account_option.username} - ', end='')
            function()

        return inner()

    def print_statistics_on_filtration(self):
        non_filtered, filtered = set(), set()
        self.get_user_url_from_file((BotOption.parameters["non_filtered_path"]))  # вычитает из файла игнор лист
        Tools.file_read((BotOption.parameters["non_filtered_path"]), non_filtered)
        Tools.file_read((BotOption.parameters["filtered_path"]), filtered)
        print(
            f'\nНе отфильтровано - {len(non_filtered)}.'
            f'\nГотовых - {len(filtered)}.',
            f'\nОтобрано в сессии - [{self.count}/{self.cycle * 50}].\n')
        self.cycle += 1

    def print_statistics_on_parce(self):
        non_filtered = set()
        Tools.file_read((BotOption.parameters["non_filtered_path"]), non_filtered)
        self.count_iteration += 1
        print(f'Успешно. В списке: {len(non_filtered)}.')

    def print_profile_page_info(self):
        username = self.account_option.user_url.split("/")[-2]
        print(f'[{self.count_iteration + 1}/{self.count_limit}] Перешёл в профиль: {username}', end=' ===> ')

    def print_unsubscribe_click_info(self):
        print(f'[{self.count_iteration}/10] - Успешно отписался.')

    @staticmethod
    def print_subscribe_limit_info():
        print(f'{Subscribe.subscribe_in_session} пользователей. ',
              f'Таймаут {Subscribe.sleep_between_iterations} минут.')

    def print_timer(self):
        print(f'Установлен таймер {self.timer} минут.')

    @staticmethod
    def print_proxy_successful_connection():
        date = datetime.now().strftime("%H:%M:%S")
        print(f'{date} Успешно подключился через прокси.', end=' ===> ')

    def print_login_not_cookie(self):
        print(f'Залогинился и создал cookie-файл ===> data/cookies/{self.account_option.username}_cookies.')

    @staticmethod
    def print_login_from_cookie():
        print('Залогинился через cookie-файл.')

    def print_subscribe_amount(self):
        print(f'Количество подписок в текущем профиле: {self.subscribes}')

    @staticmethod
    def print_start_login():
        print(f'Попытка логина.')
