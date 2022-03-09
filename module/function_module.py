from module.exception_module import FilteredOut, BotNonCriticalException, BotFinishTask
from module.message_text_module import InformationMessage
from module.filter_module import FilterClass
from selenium.webdriver.common.by import By
from selenium import webdriver
from settings import *
import time


class FunctionClass(FilterClass):
    def login(self):
        while True:
            try:
                try:
                    try:
                        self.browser = webdriver.Chrome(options=self.account_option.chrome_options)
                        if self.account_option.proxy:
                            self.check_proxy_ip()
                        self.browser.get('https://www.instagram.com/')
                        self.should_be_home_page()
                        self.cookie_login()
                        break

                    except FileNotFoundError:
                        self.not_cookie_login()
                        break

                except Exception as exception:
                    self.account_option.exception = exception
                    self.standard_exception_handling()
                    break
            except ConnectionError:
                continue

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
                self.catching_non_critical_bot_exceptions()

            except Exception as exception:
                self.account_option.exception = exception
                self.standard_exception_handling()
                self.count_iteration += 1

    def subscribe(self):
        self.go_to_my_profile_page_and_set_subscribes_amount()
        self.count_limit = Subscribe.subscribe_limit_stop - self.subscribes

        while self.count_iteration < self.count_limit:
            try:
                self.set_user_url_from_file('filtered/user_urls_subscribers.txt', 'ignore_list.txt')
                self.go_to_user_page()
                self.press_to_subscribe_button()
                self.check_limits_from_subscribe()

            except BotNonCriticalException as exception:
                self.account_option.exception = exception
                self.catching_non_critical_bot_exceptions()

            except Exception as exception:
                self.account_option.exception = exception
                self.standard_exception_handling()

        raise BotFinishTask(InformationMessage.task_finish)

    def filter(self):
        self.count_limit = Filter.iteration_for_one_account

        for self.count_iteration in range(self.count_limit):
            try:
                if self.count_iteration % 50 == 0:
                    self.get_statistics_on_filtration()

                self.set_user_url_from_file(
                    'non_filtered/subscribers_urls.txt',
                    'ignore_list.txt',
                    'filtered/user_urls_subscribers.txt')
                self.go_to_user_page()
                self.should_be_compliance_with_limits()
                self.file_write('filtered/user_urls_subscribers.txt', self.user_url)
                self.count += 1

            except BotNonCriticalException as exception:
                self.account_option.exception = exception
                self.catching_non_critical_bot_exceptions()

            except FilteredOut as exception:
                self.account_option.exception = exception
                self.bot_filter_out_handling()

            except Exception as exception:
                self.account_option.exception = exception
                self.standard_exception_handling()

            finally:
                time.sleep(Filter.timeout)

    def parce(self):

        urls_public = []
        self.file_read(self.account_option.parce_read_file_path, urls_public)
        self.count_limit = len(urls_public)
        urls_public = urls_public[self.count_iteration:-1]

        for self.user_url in urls_public:
            try:
                self.go_to_user_page()
                self.count_iteration += 1
                self.search_element((By.CSS_SELECTOR, 'li:nth-child(2) > a')).click()  # открыть список подписчиков
                self.scrolling_div_block_and_return_list_of_users(
                    (By.CSS_SELECTOR, 'div.RnEpo.Yx5HN > div > div > div> div.isgrP'),
                    count=Parce.scroll_number_subscribers_list + 1)
                user_urls = self.tag_search(ignore=self.account_option.username)
                self.file_write(self.account_option.parce_write_file_path, user_urls)
                with open(f'data/{self.account_option.parce_write_file_path}', 'r') as file:
                    size = len(file.readlines())
                    print(f'Успешно. Количество собранных пользователей: {size}.')

                if self.count_iteration % Parce.cycles_for_one_account == 0:
                    break

            except BotNonCriticalException as exception:
                self.account_option.exception = exception
                self.catching_non_critical_bot_exceptions()

            except Exception as exception:
                self.account_option.exception = exception
                self.standard_exception_handling()

        raise BotFinishTask(InformationMessage.task_finish)
