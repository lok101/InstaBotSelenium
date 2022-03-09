from module.exception_module import FilteredOut, BotNonCriticalException, BotFinishTask, ExceptionHandling
from module.message_text_module import InformationMessage
from module.filter_module import FilterClass
from selenium.webdriver.common.by import By
from module.option import BotOption
from selenium import webdriver
from settings import *
import time


class FunctionClass(FilterClass):
    def login(self):
        try:
            try:
                self.browser = webdriver.Chrome(options=self.account_option.chrome_options)
                if self.account_option.proxy:
                    self.check_proxy_ip()
                self.browser.get('https://www.instagram.com/')
                self.should_be_home_page()
                self.cookie_login()

            except FileNotFoundError:
                self.not_cookie_login()

        except Exception as exception:
            self.account_option.exception = exception
            ExceptionHandling(self.account_option).standard_exception_handling()

    def unsubscribe(self):
        while True:
            try:
                count = 10
                self.go_to_my_profile_page_and_set_subscribes_amount()
                if self.subscribes == 0:
                    raise BotFinishTask(InformationMessage.task_finish)

                self.search_element((By.XPATH, "//li[3]/a")).click()  # открыть список подписок
                following_div_block = self.search_element((By.CSS_SELECTOR, "div > div > div.isgrP > ul > div"))
                following_users = following_div_block.find_elements(By.TAG_NAME, "li")

                for user in following_users:
                    if not count:
                        time.sleep(Unsubscribe.sleep_between_iterations * 60)
                        break
                    self.press_to_unsubscribe_button_and_set_timeouts(user)
                    count -= 1

            except BotNonCriticalException as exception:
                self.account_option.exception = exception
                ExceptionHandling(self.account_option).catching_non_critical_bot_exceptions()

            except Exception as exception:
                self.account_option.exception = exception
                ExceptionHandling(self.account_option).standard_exception_handling()
                self.count_iteration += 1

    def subscribe(self):
        self.go_to_my_profile_page_and_set_subscribes_amount()
        self.set_count_limit_for_subscribe()
        while self.count_iteration < self.count_limit:
            try:
                self.set_user_url_from_file(BotOption.parameters['filtered_path'])
                self.go_to_user_page()
                self.press_to_subscribe_button()
                self.check_limits_from_subscribe()

            except BotNonCriticalException as exception:
                self.account_option.exception = exception
                ExceptionHandling(self.account_option).catching_non_critical_bot_exceptions()

            except Exception as exception:
                self.account_option.exception = exception
                ExceptionHandling(self.account_option).standard_exception_handling()

        raise BotFinishTask(InformationMessage.task_finish)

    def filter(self):
        self.count_limit = Filter.iteration_for_one_account
        for self.count_iteration in range(self.count_limit):
            try:
                if self.count_iteration % 50 == 0:
                    self.print_statistics_on_filtration()

                self.set_user_url_from_file(BotOption.parameters['non_filtered_path'])
                self.go_to_user_page()
                self.should_be_compliance_with_limits()
                self.file_write((BotOption.parameters['filtered_path']), self.user_url)
                self.count += 1

            except BotNonCriticalException as exception:
                self.account_option.exception = exception
                ExceptionHandling(self.account_option).catching_non_critical_bot_exceptions()

            except FilteredOut as exception:
                self.account_option.exception = exception
                ExceptionHandling(self.account_option).bot_filter_out_handling(self.user_url)

            except Exception as exception:
                self.account_option.exception = exception
                ExceptionHandling(self.account_option).standard_exception_handling()

            finally:
                time.sleep(Filter.timeout)

    def parce(self):
        url_list = self.get_users_url_for_parce()
        for self.user_url in url_list:
            try:
                self.go_to_user_page()
                self.search_element((By.CSS_SELECTOR, 'li:nth-child(2) > a')).click()  # открыть список подписчиков
                self.scrolling_div_block(count=Parce.scroll_number_subscribers_list + 1)
                user_urls = self.tag_search(ignore=self.account_option.username)
                self.file_write((BotOption.parameters["non_filtered_path"]), user_urls)
                self.print_statistics_on_parce()
                if self.count_iteration % Parce.cycles_for_one_account == 0:
                    break

            except BotNonCriticalException as exception:
                self.account_option.exception = exception
                ExceptionHandling(self.account_option).catching_non_critical_bot_exceptions()

            except Exception as exception:
                self.account_option.exception = exception
                ExceptionHandling(self.account_option).standard_exception_handling()

        raise BotFinishTask(InformationMessage.task_finish)
