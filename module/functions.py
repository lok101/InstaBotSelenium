from module import exception, message_text
from settings import Parce, Unsubscribe, FilterLimits

from module.service import Check, Tools, Text
from module.base_module import BaseClass
from module.support import Support
from module.filters import Filter
from module.login import Login

import time


class Function(BaseClass):
    def login(self):
        try:
            try:
                Support.go_timer(self)
                if self.account_data['proxy']:
                    Check.check_proxy_ip(self)
                Login.cookie_login(self)

            except FileNotFoundError:
                print('Логин через cookie на удался. Попытка логина через login-pass.')
                Login.not_cookie_login(self)

        except Exception as ex:
            self.account_data['exception'] = ex
            Support.standard_exception_handling(self)

    def unsubscribe(self):
        while True:
            try:
                self.count_iteration = 0
                Support.go_to_my_profile_page_and_set_subscribes_amount(self)
                if self.subscribes == 40:
                    raise exception.BotFinishTask(self, message_text.InformationMessage.task_finish)
                following_users = Support.return_subscriptions_list_for_this_account(self)
                for user in following_users:
                    if self.count_iteration == 10:
                        time.sleep(Unsubscribe.sleep_between_iterations * 60)
                        break
                    Support.press_to_unsubscribe_button_and_set_timeouts(self, user)

            except exception.BotNonCriticalException as ex:
                print(ex)

            except Exception as ex:
                self.account_data['exception'] = ex
                Support.standard_exception_handling(self)
                self.count_iteration += 1

    def subscribe(self):
        Support.go_to_my_profile_page_and_set_subscribes_amount(self)
        self.set_count_limit_for_subscribe()
        while self.count_iteration < self.count_limit:
            try:
                Tools.get_user_url_from_file(self, self.parameters['filtered_path'], difference_ignore_list=False)
                Support.go_to_user_page(self)
                Support.press_to_subscribe_button(self)
                Support.check_limits_from_subscribe(self)

            except exception.BotNonCriticalException as ex:
                print(ex)

            except Exception as ex:
                self.account_data['exception'] = ex
                Support.standard_exception_handling(self)

        raise exception.BotFinishTask(self, message_text.InformationMessage.task_finish)

    def filter(self):
        if self.count_iteration == 0:
            Support.shaffle_file_for_task(self)
        self.count_limit = FilterLimits.iteration_for_one_account
        for self.count_iteration in range(self.count_limit):
            try:
                if self.count_iteration % 50 == 0:
                    Text.print_statistics_on_filtration(self)

                Tools.get_user_url_from_file(self, self.parameters['non_filtered_path'])
                Support.go_to_user_page(self)
                Filter.should_be_compliance_with_limits(self)
                Tools.file_write(
                    (self.parameters['filtered_path']),
                    self.account_data['account_url']
                )
                Tools.file_write(
                    (self.parameters['ignore_list_path']),
                    self.account_data['account_url']
                )
                self.count += 1

            except exception.BotNonCriticalException as ex:
                print(ex)

            except exception.FilteredOut as ex:
                print(ex)

            except Exception as ex:
                self.account_data['exception'] = ex
                Support.standard_exception_handling(self)

            finally:
                time.sleep(FilterLimits.timeout)

    def parce(self):
        if self.count_iteration == 0:
            Support.shaffle_file_for_task(self)
        url_list = Support.get_users_url_for_parce(self)
        for self.account_data['account_url'] in url_list:
            try:
                Support.go_to_user_page(self)
                Support.save_to_file_accounts_followers(self)
                if self.count_iteration % Parce.cycles_for_one_account == 0:
                    break

            except exception.BotNonCriticalException as ex:
                print(ex)

            except Exception as ex:
                self.account_data['exception'] = ex
                Support.standard_exception_handling(self)
