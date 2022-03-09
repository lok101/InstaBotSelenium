from module.function_module import FunctionClass
from module.exception_module import BotCriticalException, BotFinishTask
import data


def bot():
    my_bot = StartBot()
    my_bot.start()


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
                    self.account_option.exception = exception
                    self.catching_critical_bot_exceptions()

        except BotFinishTask as exception:
            self.account_option.exception = exception
            self.catching_critical_bot_exceptions()

        finally:
            if self.browser is not None:
                self.browser.quit()


if __name__ == '__main__':
    bot()
