from datetime import datetime
from module import base_module
from module.option import BotOption
from module.tools import Tools
from settings import Subscribe, StartSettings


class Print(base_module.BaseClass):
    @staticmethod
    def print_to_console(*args):
        def inner():
            for function in args:
                function()

        return inner()

    @staticmethod
    def current_time():
        print(f'{datetime.now().strftime("%H:%M:%S")} - ', end='')

    def account_name(self):
        print(f'{self.account_option.account_data["user_name"]} - ', end='')

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

    def profile_page_info(self):
        username = self.account_option.user_url.split("/")[-2]
        print(f'[{self.count_iteration + 1}/{self.count_limit}] Перешёл в профиль: {username}', end=' ===> ')

    def unsubscribe_click_info(self):
        print(f'[{self.count_iteration}/10] - Успешно отписался.')

    @staticmethod
    def subscribe_limit_info():
        print(f'Подписался на очередные {Subscribe.subscribe_in_session} пользователей. ',
              f'Таймаут {Subscribe.sleep_between_iterations} минут.')

    def print_timer(self):
        print(f'Установлен таймер {self.account_option.timer} минут.')

    @staticmethod
    def proxy_successful_connection():
        date = datetime.now().strftime("%H:%M:%S")
        print(f'{date} Успешно подключился через прокси.', end=' ===> ')

    def login_not_cookie(self):
        print(f'Залогинился и создал cookie-файл ===> '
              f'data/cookies/{self.account_option.account_data["user_name"]}_cookies.')

    @staticmethod
    def login_from_cookie():
        print('Залогинился через cookie-файл.')

    def subscribe_amount(self):
        print(f'Количество подписок в текущем профиле: {self.subscribes}')

    @staticmethod
    def start_login():
        print(f'Попытка логина.')

    @staticmethod
    def subscribe_successful():
        print('Успешно подписался.')

    @staticmethod
    def button_not_found():
        print('Кнопка не найдена.')

    def connection_failed(self):
        timeout = StartSettings.err_proxy_timeout
        print(f'{self.account_option.mode} >> CONNECTION_FAILED. Запись добавлена в лог. Таймаут {timeout} секунд.')

    def exception_info(self):
        exception_name = str(type(self.account_option.exception)).split("'")[1].split('.')[-1]
        print(f'\nИсключение обработано и добавлено в лог: {self.account_option.mode}/{exception_name}')

    @staticmethod
    def shuffle_parce_file():
        print(f'Файл {BotOption.parameters["parce_url_path"]} - перемешан.')

    @staticmethod
    def shuffle_filter_file():
        print(f'Файл {BotOption.parameters["non_filtered_path"]} - перемешан.')

