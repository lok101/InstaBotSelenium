from module.function_module import FunctionClass
from module import exception_module


class StartBot(FunctionClass):
    def start(self):
        try:
            self.account_option.input_operating_mode_and_set_parameters()
            self.account_option.set_browser_parameters()
            self.account_option.input_account_and_set_accounts_list()

            for name in self.account_option.accounts_key_number:
                try:
                    self.account_option.set_account_parameters(name)
                    try:
                        self.login_check()
                        self.go_to_my_profile_page_from_click()
                    except exception_module.LoginError:
                        self.login()
                    eval(f'self.{self.account_option.mode}()')
                    self.browser.quit()
                except exception_module.BotCriticalException as exception:
                    print(exception)

        except exception_module.BotFinishTask as exception:
            print(exception)

        finally:
            if self.browser is not None:
                self.browser.quit()


if __name__ == '__main__':
    my_bot = StartBot()
    my_bot.start()
