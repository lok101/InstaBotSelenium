from data import user_dict
from module.function_module import FunctionClass
from settings import StartSettings
import random

operating_status = input('Укажите режим работы: ')
if operating_status == 'fil':
    try:
        headless_and_proxy = input('Headless(y/n) Proxy(y/n): ')
        for i in range(StartSettings.number_filter_iteration):
            try:
                user = f'test{random.randrange(1, 7)}'
                print(f'Бот аккаунт - {user}', end=' =====> ')
                username = user_dict[user]['login']
                password = user_dict[user]['password']
                my_bot = FunctionClass(username, password, headless_and_proxy)
                my_bot.login()
                my_bot.filter_user_list(user)
                my_bot.close_browser()
            except AssertionError:
                input('Пауза')
                continue
    finally:
        my_bot.close_browser()
else:
    user_input = input('Введите имя аккаунта: ')
    username = user_dict[user_input]['login']
    password = user_dict[user_input]['password']
    headless_and_proxy = input('Headless(y/n) Proxy(y/n): ')
    my_bot = FunctionClass(username, password, headless_and_proxy)

    try:
        my_bot.login()
        if operating_status == 'sub':
            my_bot.subscribe_to_user_list(username)
        elif operating_status == 'uns':
            my_bot.unsubscribe_for_all_users(username)
        elif operating_status == 'sel':
            my_bot.select_subscribes(username)
    finally:
        my_bot.close_browser()
