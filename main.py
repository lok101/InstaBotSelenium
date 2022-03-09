from module.function_module import FunctionClass
from module.exception_module import BotCriticalException, BotFinishTask
from settings import AccountSettings
import data


def bot():
    my_bot = StartBot()
    my_bot.start()


class StartBot(FunctionClass):
    def start(self):
        try:
            self.input_operating_mode_and_set_parameters()
            self.set_browser_parameters()
            self.input_account_and_set_accounts_list()

            for name in AccountSettings.accounts_key_number:
                try:
                    self.username = data.user_dict[f'{AccountSettings.accounts_key_mask}-{name}']['login']
                    self.password = data.user_dict[f'{AccountSettings.accounts_key_mask}-{name}']['password']
                    self.login()
                    eval(f'self.{self.AccountSettings}()')
                    self.browser.quit()
                except BotCriticalException as exception:
                    self.exception = exception
                    self.catching_critical_bot_exceptions()

        except BotFinishTask as exception:
            self.exception = exception
            self.catching_critical_bot_exceptions()

        finally:
            if self.browser is not None:
                self.browser.quit()


if __name__ == '__main__':
    bot()
