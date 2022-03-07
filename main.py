from module.function_module import FunctionClass
from module.exception_module import BotCriticalException, BotFinishTask
import data


def bot():
    my_bot = StartBot()
    my_bot.start()


class StartBot(FunctionClass):
    def start(self):
        try:
            self.parameter_input_and_set()
            self.browser_parameter_set()
            self.accounts_input()

            for name in self.accounts_key_number:
                try:
                    self.username = data.user_dict[f'{self.accounts_key_mask}-{name}']['login']
                    self.password = data.user_dict[f'{self.accounts_key_mask}-{name}']['password']
                    self.login()
                    eval(f'self.{self.mode}()')
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
