from module.functions import FunctionClass
from module import exception, tools


class StartBot(FunctionClass):
    def start(self):
        try:
            self.account_option.get_accounts_list()
            self.account_option.set_browser_parameters()
            for account_id in self.account_option.accounts_key_number_list:
                try:
                    self.account_option.set_account_parameters_by_db(account_id)
                    self.account_option.get_user_agent(account_id)
                    self.login()
                    eval(f'self.{self.account_option.mode}()')
                    self.browser.quit()
                except exception.BotCriticalException as ex:
                    print(ex)

        except exception.BotFinishTask as ex:
            print(ex)

        finally:
            if self.browser is not None:
                self.browser.quit()


if __name__ == '__main__':
    # tools.Tools.add_accounts_to_data_base()
    my_bot = StartBot()
    my_bot.start()
