from data import user_dict, bot_dict
from module.function_module import FunctionClass
from settings import SearchUser
from module.base_module import LoginError
import random
import time


def bot():
    while True:
        try:
            operating_status = input('Укажите режим работы: ')
            if operating_status == 'fil':
                filter_user_list()

            elif operating_status == 'sub':
                subscribe_to_user_list()

            elif operating_status == 'uns':
                unsubscribe_for_all_users()

            elif operating_status == 'sel':
                select_subscribers()

            else:
                raise NameError('Неверный режим работы.')
        except NameError:
            continue


def filter_user_list():
    try:
        headless_and_proxy = input('Headless(y/n) Proxy(y/n): ')
        for i in range(SearchUser.number_restart_filtered):
            try:
                user = f'bot{random.randrange(1, len(bot_dict))}'
                print(f'Бот аккаунт - {user}', end=' =====> ')
                username = bot_dict[user]['login']
                password = bot_dict[user]['password']
                my_bot = FunctionClass(username, password, headless_and_proxy)
                my_bot.login()
                my_bot.filter_user_list()
                my_bot.close_browser()
                time.sleep(SearchUser.timeout_between_restarts * 60)
            except AssertionError:
                continue
            except LoginError:
                continue
    finally:
        my_bot.close_browser()


def select_subscribers():
    try:
        headless_and_proxy = input('Headless(y/n) Proxy(y/n): ')
        with open('data/url_lists/public_url_for_subscribe.txt', 'r') as file:
            iteration_number = len(file.readlines())//10
        with open('data/non_filtered/user_urls_subscribers.txt', 'w'):
            print('Файл очищен.')
        for iter_count in range(iteration_number):
            try:
                user = f'bot{random.randrange(1, len(bot_dict) + 1)}'
                print(f'Бот аккаунт - {user}', end=' =====> ')
                username = bot_dict[user]['login']
                password = bot_dict[user]['password']
                my_bot = FunctionClass(username, password, headless_and_proxy)
                my_bot.login()
                my_bot.select_subscribers(iter_count)
                my_bot.close_browser()
            except Exception as error:
                print(error)
            finally:
                continue
    finally:
        my_bot.close_browser()


def subscribe_to_user_list():
    try:
        account_list = []
        user_input = input('Введите имя аккаунта: ')
        headless_and_proxy = input('Headless(y/n) Proxy(y/n): ')

        for i in range(user_input.count(' ') + 1):
            account_list.append(user_input.split(' ')[i])

        for user in account_list:
            username = user_dict[user]['login']
            password = user_dict[user]['password']
            my_bot = FunctionClass(username, password, headless_and_proxy)
            my_bot.login()
            my_bot.subscribe_to_user_list()
            my_bot.close_browser()
    finally:
        my_bot.close_browser()


def unsubscribe_for_all_users():
    try:
        user_input = input('Введите имя аккаунта: ')
        username = user_dict[user_input]['login']
        password = user_dict[user_input]['password']
        headless_and_proxy = input('Headless(y/n) Proxy(y/n): ')
        my_bot = FunctionClass(username, password, headless_and_proxy)
        my_bot.login()
        my_bot.unsubscribe_for_all_users()
        my_bot.close_browser()
    finally:
        my_bot.close_browser()


if __name__ == '__main__':
    bot().run()
