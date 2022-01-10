from data import user_dict
from module.function_module import FunctionClass

operating_status = input('Укажите режим работы: ')
if operating_status == 'fil':
    try:
        headless_and_proxy = input('Headless(y/n) Proxy(y/n): ')
        for user, user_data in user_dict.items():
            username = user_data['login']
            password = user_data['password']
            my_bot = FunctionClass(username, password, headless_and_proxy)
            my_bot.login()
            my_bot.filter_user_list()
            my_bot.close_browser()
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
            my_bot.subscribe_to_user_list()
        elif operating_status == 'uns':
            my_bot.unsubscribe_for_all_users()
        elif operating_status == 'sel':
            my_bot.select_subscribes()
        elif operating_status == 'fil':
            my_bot.filter_user_list()
    finally:
        my_bot.close_browser()
