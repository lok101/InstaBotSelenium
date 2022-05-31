from module.functions import Function
from module import exception
from module.service import Tools


class StartBot(Function):
    def start(self):
        try:
            self.input_mode_and_set_working_parameters()
            account_list = self.get_accounts_list()
            self.set_browser_parameters()
            for account_id in account_list:
                try:
                    self.set_account_parameters_by_db(account_id)
                    self.get_user_agent(account_id)
                    self.login()
                    eval(f'self.{self.account_data["WORK_MODE"]}()')
                    self.browser.quit()
                except exception.BotCriticalException as ex:
                    print(ex)

        except exception.BotFinishTask as ex:
            print(ex)

        finally:
            if self.browser is not None:
                self.browser.quit()


if __name__ == '__main__':
    Tools.add_accounts_to_data_base()
    my_bot = StartBot()
    my_bot.start()
