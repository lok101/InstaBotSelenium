import settings
from module.function_module import FunctionClass
from module.exception_module import BotException
from settings import SearchUser
import data
import random
import time


def bot():
    my_bot = StartBot()
    my_bot.start()


def GUI_start(account, mode):
    print(f'Задача {mode} для аккаунта {account} запущена.')


class StartBot(FunctionClass):
    def start(self):
        try:
            self.parameter_input()
            self.browser_parameter()
            eval(f'self.start_{self.working_mode}()')

        except KeyboardInterrupt:
            print('Остановлено командой с клавиатуры.')
        finally:
            if self.browser is not None:
                self.close_browser()

    def start_unsubscribe(self):
        try:
            user_input = input('Введите имя аккаунта: ')
            self.username = data.user_dict[user_input]['login']
            self.password = data.user_dict[user_input]['password']
            self.login()
            self.unsubscribe_for_all_users()
            self.close_browser()
        except BotException as ex:
            self.exception_text = str(type(ex)).split("'")[1].split('.')[-1]
            self.print_and_save_log_traceback()

    def start_subscribe(self):
        account_list = []
        user_input = input('Введите имя аккаунта: ')
        for i in range(user_input.count(' ') + 1):
            account_list.append(user_input.split(' ')[i])
        for user in account_list:
            try:
                self.username = data.user_dict[user]['login']
                self.password = data.user_dict[user]['password']
                self.login()
                self.subscribe_to_user_list()
                self.close_browser()
            except BotException as ex:
                self.exception_text = str(type(ex)).split("'")[1].split('.')[-1]
                self.print_and_save_log_traceback()
                continue

    def start_short_subscribe(self):
        cycle_count = settings.ShortSubscribe.subscribe_limit_stop // settings.ShortSubscribe.subscribe_in_session
        for self.cycle in range(cycle_count):
            for account in range(len(data.preparatory_account)):
                try:
                    print(f'Аккаунт [{account + 1}/{len(data.preparatory_account)}]', end=' -- ')
                    self.username = data.preparatory_account[str(account)]['login']
                    self.password = data.preparatory_account[str(account)]['password']
                    self.login()
                    self.short_subscribe()
                    self.close_browser()
                except BotException as ex:
                    self.exception_text = str(type(ex)).split("'")[1].split('.')[-1]
                    self.print_and_save_log_traceback()
                    continue

    def start_selection(self):
        with open(f'data/{self.read_file_path}', 'r') as file:
            iteration_number = len(file.readlines()) // 10
        with open(f'data/{self.write_file_path}', 'w'):
            print('Файл очищен.')
        for iter_count in range(iteration_number):
            try:
                user = f'bot{random.randrange(1, len(data.bot_dict) + 1)}'
                print(f'Бот аккаунт - {user}', end=' =====> ')
                self.username = data.bot_dict[user]['login']
                self.password = data.bot_dict[user]['password']
                self.login()
                self.select_subscribers(iter_count)
                self.close_browser()
            except BotException as ex:
                self.exception_text = str(type(ex)).split("'")[1].split('.')[-1]
                self.print_and_save_log_traceback()
                continue

    def start_filtered(self):
        for i in range(SearchUser.number_restart_filtered):
            try:
                user = f'bot{random.randrange(1, len(data.bot_dict))}'
                print(f'Бот аккаунт - {user}', end=' =====> ')
                self.username = data.bot_dict[user]['login']
                self.password = data.bot_dict[user]['password']
                self.login()
                self.filter_user_list()
                self.close_browser()
                time.sleep(SearchUser.timeout_between_restarts * 60)
            except BotException as ex:
                self.exception_text = str(type(ex)).split("'")[1].split('.')[-1]
                self.print_and_save_log_traceback()
                continue


if __name__ == '__main__':
    bot()
