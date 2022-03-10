from module.exception_module import BotCriticalException, BotFinishTask
from module.function_module import FunctionClass
import data


class StartBot(FunctionClass):
    def start(self):
        try:
            self.account_option.input_operating_mode_and_set_parameters()
            self.account_option.set_browser_parameters()
            self.account_option.input_account_and_set_accounts_list()

            for name in self.account_option.accounts_key_number:
                try:
                    self.account_option.username = data.user_dict[
                        f'{self.account_option.accounts_key_mask}-{name}']['login']
                    self.account_option.password = data.user_dict[
                        f'{self.account_option.accounts_key_mask}-{name}']['password']
                    self.login()
                    eval(f'self.{self.account_option.mode}()')
                    self.browser.quit()
                except BotCriticalException as exception:
                    print(exception)

        except BotFinishTask as exception:
            print(exception)

        finally:
            if self.browser is not None:
                self.browser.quit()


if __name__ == '__main__':
    my_bot = StartBot()
    my_bot.start()
