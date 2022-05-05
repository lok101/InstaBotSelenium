from module import exception
from module import navigation
from module import login
from module.message_text import InformationMessage
from settings import Parce, Unsubscribe, Filter
from module.filters import FilterClass
from selenium.webdriver.common.by import By
from module.option import BotOption
from module.tools import Tools
import time


class FunctionClass(FilterClass, login.Login, navigation.Navigation):
    def login(self):
        try:
            try:
                self.go_timer()
                if self.account_option.proxy:
                    self.check_proxy_ip()
                self.cookie_login()

            except FileNotFoundError:
                print('Логин через cookie на удался. Попытка логина через login-pass.')
                self.not_cookie_login()

        except Exception as ex:
            self.account_option.exception = ex
            self.standard_exception_handling()

    def unsubscribe(self):
        while True:
            try:
                self.count_iteration = 0
                self.go_to_my_profile_page_and_set_subscribes_amount()
                if self.subscribes == 0:
                    raise exception.BotFinishTask(self.account_option, InformationMessage.task_finish)

                self.search_element((By.XPATH, "//li[3]/a")).click()  # открыть список подписок
                following_div_block = self.search_element((By.CSS_SELECTOR, "div > div > div.isgrP > ul > div"))
                following_users = following_div_block.find_elements(By.TAG_NAME, "li")

                for user in following_users:
                    if self.count_iteration == 10:
                        time.sleep(Unsubscribe.sleep_between_iterations * 60)
                        break
                    self.press_to_unsubscribe_button_and_set_timeouts(user)

            except exception.BotNonCriticalException as ex:
                print(ex)

            except Exception as ex:
                self.account_option.exception = ex
                self.standard_exception_handling()
                self.count_iteration += 1

    def subscribe(self):
        self.go_to_my_profile_page_and_set_subscribes_amount()
        self.set_count_limit_for_subscribe()
        while self.count_iteration < self.count_limit:
            try:
                self.get_user_url_from_file(BotOption.parameters['filtered_path'], difference_ignore_list=False)
                self.go_to_user_page()
                self.press_to_subscribe_button()
                self.check_limits_from_subscribe()

            except exception.BotNonCriticalException as ex:
                print(ex)

            except Exception as ex:
                self.account_option.exception = ex
                self.standard_exception_handling()

        raise exception.BotFinishTask(self.account_option, InformationMessage.task_finish)

    def filter(self):
        if self.count_iteration == 0:
            self.shaffle_file_for_task()
        self.count_limit = Filter.iteration_for_one_account
        for self.count_iteration in range(self.count_limit):
            try:
                if self.count_iteration % 50 == 0:
                    self.print_statistics_on_filtration()

                self.get_user_url_from_file(BotOption.parameters['non_filtered_path'])
                self.go_to_user_page()
                self.should_be_compliance_with_limits()
                Tools.file_write((BotOption.parameters['filtered_path']), self.account_option.user_url)
                Tools.file_write((BotOption.parameters['ignore_list_path']), self.account_option.user_url)
                self.count += 1

            except exception.BotNonCriticalException as ex:
                print(ex)

            except exception.FilteredOut as ex:
                print(ex)

            except Exception as ex:
                self.account_option.exception = ex
                self.standard_exception_handling()

            finally:
                time.sleep(Filter.timeout)

    def parce(self):
        if self.count_iteration == 0:
            self.shaffle_file_for_task()
        url_list = self.get_users_url_for_parce()
        for self.account_option.user_url in url_list:
            try:
                self.go_to_user_page()
                self.search_element((By.CSS_SELECTOR, 'li:nth-child(2) > a')).click()  # открыть список подписчиков
                self.scrolling_div_block(count=Parce.scroll_number_subscribers_list + 1)
                user_urls = self.tag_search(ignore=self.account_option.username)
                Tools.file_write((BotOption.parameters["non_filtered_path"]), user_urls)
                self.print_statistics_on_parce()
                if self.count_iteration % Parce.cycles_for_one_account == 0:
                    break

            except exception.BotNonCriticalException as ex:
                print(ex)

            except Exception as ex:
                self.account_option.exception = ex
                self.standard_exception_handling()
