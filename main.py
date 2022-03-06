import settings
from module.function_module import FunctionClass
from module.exception_module import BotCriticalException, BotFinishTask
from settings import SearchUser
import data
import random
import time


def bot():
    my_bot = StartBot()
    my_bot.start()


class StartBot(FunctionClass):
    def start(self):
        try:
            self.parameter_input_and_set()
            self.browser_parameter_set()
            eval(f'self.start_{self.working_mode}()')

        except BotFinishTask as exception:
            self.exception = exception
            self.bot_final_task_exception_handling()

        finally:
            if self.browser is not None:
                self.browser.quit()

    def start_unsubscribe(self):
        try:
            user_input = input('Введите имя аккаунта: ')
            self.username = data.user_dict[user_input]['login']
            self.password = data.user_dict[user_input]['password']
            self.login()
            self.unsubscribe_for_all_users()
            self.browser.quit()
        except BotCriticalException as exception:
            self.exception = exception
            self.bot_critical_exception_handling()

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
                self.browser.quit()
            except BotCriticalException as exception:
                self.exception = exception
                self.bot_critical_exception_handling()

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
                    self.browser.quit()
                except BotCriticalException as exception:
                    self.exception = exception
                    self.bot_critical_exception_handling()

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
                self.browser.quit()
            except BotCriticalException as exception:
                self.exception = exception
                self.bot_critical_exception_handling()

    def start_filtered(self):
        for i in range(SearchUser.number_restart_filtered):
            try:
                user = f'bot{random.randrange(1, len(data.bot_dict))}'
                print(f'Бот аккаунт - {user}', end=' =====> ')
                self.username = data.bot_dict[user]['login']
                self.password = data.bot_dict[user]['password']
                self.login()
                self.filter_user_list()
                self.browser.quit()
                time.sleep(SearchUser.timeout_between_restarts * 60)
            except BotCriticalException as exception:
                self.exception = exception
                self.bot_critical_exception_handling()


if __name__ == '__main__':
    bot()
