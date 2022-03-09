from module.exception_module import BotCriticalException, BotException
from selenium import webdriver
from data import *
import random


class BotOption:
    def __init__(self):
        self.username = None
        self.password = None
        self.parce_read_file_path = 'url_lists/subscribers_urls.txt'
        self.parce_write_file_path = 'non_filtered/subscribers_urls.txt'
        self.headless = True
        self.proxy = True
        self.accounts_key_mask = None
        self.accounts_key_number = None
        self.chrome_options = None
        self.load_strategy = True
        self.mode = None
        self.exception = None
        self.exception_text = None

    def set_browser_parameters(self):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--log-level=3')
        self.chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        if self.headless is True:
            self.chrome_options.add_argument("--headless")
        if self.proxy is True:
            self.chrome_options.add_argument(f'--proxy-server={proxy_list}')
        if self.load_strategy is True:
            self.chrome_options.page_load_strategy = 'eager'

    def set_mode_and_mask_parameters(self, parameter_name: str):
        self.mode = parameters[parameter_name]
        self.mode = parameters[parameter_name]
        if self.mode == parameters['sub'] or self.mode == parameters['uns']:
            self.accounts_key_mask = 'main_account'
        elif self.mode == parameters['fil'] or self.mode == parameters['par']:
            self.accounts_key_mask = 'bot_account'
        else:
            raise BotCriticalException('Неизвестный режим работы, не могу установить маску аккаунта.')

    def input_operating_mode_and_set_parameters(self):
        user_input = input('Укажите режим работы (-параметры): ')
        self.set_mode_and_mask_parameters(user_input.split(' ')[0])
        if '-p' in user_input:
            self.proxy = False
        if '-h' in user_input:
            self.headless = False
        if '-e' in user_input:
            self.load_strategy = False
        if '-bot' in user_input:
            self.accounts_key_mask = 'bot_account'
        if '-main' in user_input:
            self.accounts_key_mask = 'main_account'

    def input_account_and_set_accounts_list(self):
        account_list = []
        if self.accounts_key_mask == 'main_account':
            user_input = input('Введите имя аккаунта: ')
            account_list = user_input.split(' ')

        elif self.accounts_key_mask == 'bot_account':
            for key in user_dict:
                if 'bot_account' in key:
                    account_list.append(key.split('-')[1])
            random.shuffle(account_list)
        else:
            raise BotException('Неизвестная маска аккаунта.')

        self.accounts_key_number = account_list
