from data import user_dict, tag_list, bot_dict
from module.function_module import FunctionClass
from settings import SearchUser
import random
import time


def filter_user_list():
    try:
        headless_and_proxy = input('Headless(y/n) Proxy(y/n): ')
        for i in range(SearchUser.number_restart_filtered):
            try:
                user = f'bot{random.randrange(1, len(bot_dict))}'
                print(f'Бот аккаунт - {user}', end=' =====> ')
                username = bot_dict[user]['login']
                password = bot_dict[user]['password']
                # input('====ПАУЗА====')
                my_bot = FunctionClass(username, password, headless_and_proxy)
                my_bot.login()
                my_bot.filter_user_list(user, i)
                my_bot.close_browser()
                time.sleep(SearchUser.timeout_between_restarts * 60)
            except AssertionError:
                continue
    finally:
        my_bot.close_browser()


def select_subscribers():
    try:
        headless_and_proxy = input('Headless(y/n) Proxy(y/n): ')
        for i in range(len(tag_list)):
            try:
                user = f'bot{random.randrange(1, len(bot_dict) + 1)}'
                print(f'Бот аккаунт - {user}', end=' =====> ')
                username = bot_dict[user]['login']
                password = bot_dict[user]['password']
                tag_search = tag_list[i]
                my_bot = FunctionClass(username, password, headless_and_proxy)
                my_bot.login()
                my_bot.select_subscribes(username, tag_search)
                my_bot.close_browser()
            except AssertionError:
                continue
    finally:
        my_bot.close_browser()


def subscribe_to_user_list():
    try:
        user_input = input('Введите имя аккаунта: ')
        username = user_dict[user_input]['login']
        password = user_dict[user_input]['password']
        headless_and_proxy = input('Headless(y/n) Proxy(y/n): ')
        my_bot = FunctionClass(username, password, headless_and_proxy)
        my_bot.login()
        my_bot.subscribe_to_user_list(username)
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
        my_bot.unsubscribe_for_all_users(username)
        my_bot.close_browser()
    finally:
        my_bot.close_browser()


while True:
    try:
        operating_status = input('Укажите режим работы: ')
        if operating_status == 'fil':
            filter_user_list()

        elif operating_status == 'sel':
            select_subscribers()

        elif operating_status == 'sub':
            subscribe_to_user_list()

        elif operating_status == 'uns':
            unsubscribe_for_all_users()

        else:
            raise NameError('Неверный режим работы.')
    except NameError:
        continue
