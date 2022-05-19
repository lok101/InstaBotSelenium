from selenium import webdriver
import settings
import random
import data
from module import data_base, user_agents


class BotOption:
    parameters = {
        'sub': 'subscribe',
        'uns': 'unsubscribe',
        'fil': 'filter',
        'par': 'parce',
        'short': 'short_subscribe',
        'test': 'test',
        'ignore_list_path': 'ignore_list.txt',
        'parce_url_path': 'url_lists/subscribers_urls.txt',
        'non_filtered_path': 'non_filtered/subscribers_urls.txt',
        'filtered_path': 'filtered/subscribers_urls.txt',
    }

    def __init__(self):
        self.account_data = None

        self.accounts_key_number_list = 'Номер аккаунта не присвоен.'
        self.chrome_options = None
        self.mode = 'Режим не присвоен.'
        self.second_mode = 'Дополнительный режим не присвоен.'
        self.user_url = None
        self.timer = 0

        self.exception = None
        self.exception_text = None

        self.headless = True
        self.proxy = True
        self.load_strategy = True

    def set_browser_parameters(self):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--log-level=3')
        self.chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        if self.headless is True:
            self.chrome_options.add_argument("--headless")
        if self.proxy is True:
            self.chrome_options.add_argument(f'--proxy-server={data.proxy_list}')
        if self.load_strategy is True:
            self.chrome_options.page_load_strategy = 'eager'

    def get_accounts_list(self):
        user_input_mode = self.input_operating_mode_and_set_parameters()
        accounts_type = self.set_working_mode_and_type_account(user_input_mode.split(' ')[0])
        self.input_account_and_set_accounts_list_db(accounts_type)

    def set_account_parameters_by_db(self, account_id):
        self.account_data = data_base.get_account_field_data(account_id)

    def set_working_mode_and_type_account(self, parameter_name: str):
        self.mode = BotOption.parameters[parameter_name]
        if self.mode == BotOption.parameters['sub'] \
                or self.mode == BotOption.parameters['uns'] \
                or self.mode == BotOption.parameters['test']:
            accounts_type = 'main'

        elif self.mode == BotOption.parameters['fil'] \
                or self.mode == BotOption.parameters['par']:
            accounts_type = 'bot'
        else:
            raise Exception('Неизвестный режим работы, не могу установить маску аккаунта.')

        return accounts_type

    def input_operating_mode_and_set_parameters(self):
        user_input = input('Укажите режим работы (-параметры): ')
        user_input = f'{user_input} {settings.StartSettings.default_parameters}'

        for param in user_input.split(' '):
            if '-p' in param:
                self.proxy = not self.proxy
            elif '-h' in param:
                self.headless = not self.headless
            elif '-e' in param:
                self.load_strategy = not self.load_strategy
            elif '-t' in param:
                self.timer = param.split('-t')[1].split(' ')[0]

            elif '-nonfilt' in user_input:
                self.parameters['filtered_path'] = self.parameters['non_filtered_path']

        return user_input

    def input_account_and_set_accounts_list_db(self, accounts_type):
        if accounts_type == 'main':
            self.accounts_key_number_list = input('Введите ID аккаунта: ')
        elif accounts_type == 'bot':
            accounts_key_number_list = data_base.get_accounts_id_on_status('bot')
            random.shuffle(accounts_key_number_list)
            self.accounts_key_number_list = accounts_key_number_list

    def get_user_agent(self, account_id):
        user_agent_of_account = self.account_data['user_agent']
        if user_agent_of_account is not None:
            user_agent_of_account = f'user-agent={user_agent_of_account}'
        else:
            new_user_agent = random.choice(user_agents.user_agents)
            data_base.set_value_user_agent_field(account_id, new_user_agent)
            user_agent_of_account = f'user-agent={new_user_agent}'
            print(f'Присвоен новый UserAgent: {new_user_agent}')
        self.chrome_options.add_argument(user_agent_of_account)
