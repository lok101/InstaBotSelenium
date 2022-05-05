from module.functions import FunctionClass
from module import exception


class StartBot(FunctionClass):
    def start(self):
        try:
            self.account_option.input_operating_mode_and_set_parameters()
            self.account_option.set_browser_parameters()
            self.account_option.input_account_and_set_accounts_list()

            for name in self.account_option.accounts_key_number:
                try:
                    self.account_option.set_account_parameters(name)
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
    my_bot = StartBot()
    my_bot.start()
