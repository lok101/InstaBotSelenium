from settings import Subscribe, Unsubscribe, StartSettings, Parce
from module import exception, message_text, page_checkup, selectors
from module.option import BotOption
from module.tools import Tools
from datetime import datetime
import traceback
import random
import time


class Support(page_checkup.Checks):
    def press_to_subscribe_button(self):
        self.search_element(selectors.UserPage.all_buttons)  # выполняет роль проверки на загрузку
        buttons = self.browser.find_elements(selectors.UserPage.all_buttons)
        for button in buttons:
            if 'подписаться' in button.text.lower():
                iteration_limit = 10
                iteration_count = 0
                while iteration_count < iteration_limit:
                    iteration_count += 1
                    button.click()
                    time.sleep(random.randrange(Subscribe.min_timeout, Subscribe.max_timeout))
                    self.should_be_subscribe_and_unsubscribe_blocking()
                    Tools.file_write((BotOption.parameters["ignore_list_path"]), self.account_option.user_url)
                    self.count_iteration += 1
                    self.print_to_console(
                        self.subscribe_successful)
                    return
        self.print_to_console(
            self.button_not_found)
        Tools.file_write((BotOption.parameters["ignore_list_path"]), self.account_option.user_url)
        time.sleep(random.randrange(Subscribe.min_timeout, Subscribe.max_timeout))

    def check_limits_from_subscribe(self):
        if self.count_iteration % Subscribe.subscribe_in_session == 0 and self.count_iteration != 0:
            self.go_to_my_profile_page_and_set_subscribes_amount()
            self.print_to_console(
                self.current_time,
                self.account_name,
                self.subscribe_limit_info)
            time.sleep(Subscribe.sleep_between_iterations * 60)

    def press_to_unsubscribe_button_and_set_timeouts(self, user):
        user.find_element(selectors.UserPage.all_buttons).click()  # нажать кнопку отписки
        time.sleep(random.randrange(Unsubscribe.min_sleep, Unsubscribe.max_sleep))
        self.search_element(selectors.UserPage.button_confirm_unsubscribe).click()  # нажать кнопку подтверждения
        self.should_be_subscribe_and_unsubscribe_blocking()
        self.count_iteration += 1
        self.print_to_console(
            self.current_time,
            self.account_name,
            self.unsubscribe_click_info)

    def go_to_user_page(self):
        self.browser.get(self.account_option.user_url)
        self.print_to_console(
            self.current_time,
            self.account_name,
            self.profile_page_info)

        self.should_be_instagram_page()
        self.should_be_verification_form()
        self.should_be_user_page()
        self.should_be_activity_blocking()

    def go_to_my_profile_page_and_set_subscribes_amount(self):
        url = f'https://www.instagram.com/{self.account_option.username}/'
        self.browser.get(url)
        self.should_be_instagram_page()
        self.should_be_activity_blocking()
        self.should_be_verification_form()

        self.subscribes = self.return_amount_posts_subscribes_and_subscribers()['subs']
        self.print_to_console(
            self.current_time,
            self.account_name,
            self.subscribe_amount)

    def get_users_url_for_parce(self):
        urls_public = []
        Tools.file_read((BotOption.parameters["parce_url_path"]), urls_public)
        self.count_limit = len(urls_public)
        if self.count_iteration + 1 >= self.count_limit:
            raise exception.BotFinishTask(
                self.account_option,
                message_text.InformationMessage.task_finish)
        urls_public = urls_public[self.count_iteration:-1]
        return urls_public

    def go_timer(self):
        if self.account_option.timer != 0:
            self.print_to_console(
                self.current_time,
                self.account_name,
                self.print_timer)
            time.sleep(int(self.account_option.timer) * 60)

    def standard_exception_handling(self):
        self.save_log_exception()
        if self.account_option.mode == self.account_option.parameters['fil'] \
                and isinstance(self.account_option.exception, KeyError):
            raise exception.BotFinishTask(
                self.account_option,
                message_text.FilterMessage.list_empty)
        self.print_to_console(
            self.exception_info)

    def save_log_exception(self):
        exception_name = str(type(self.account_option.exception)).split("'")[1].split('.')[-1]
        path = f'logs/{self.account_option.mode}/{exception_name}.txt'

        date = datetime.now().strftime("%d-%m %H:%M:%S")
        exception_text = traceback.format_exc()
        log_text = f'{date}\n{exception_text}\n\n'

        Tools.file_write(path, log_text)

        if 'CONNECTION_FAILED' in exception_text:
            self.print_to_console(
                self.current_time,
                self.account_name,
                self.connection_failed)
            time.sleep(StartSettings.err_proxy_timeout)

    def shaffle_file_for_task(self):
        if self.account_option.mode == BotOption.parameters['par']:
            Tools.shaffle_file(BotOption.parameters['parce_url_path'])
            self.print_to_console(
                self.current_time,
                self.account_name,
                self.shuffle_parce_file)
        elif self.account_option.mode == BotOption.parameters['fil']:
            Tools.shaffle_file(BotOption.parameters['non_filtered_path'])
            self.print_to_console(
                self.current_time,
                self.account_name,
                self.shuffle_filter_file)
        else:
            raise Exception('Неизвестный режим в методе "shaffle_file_for_task".')

    def return_subscriptions_list_for_this_account(self):
        self.search_element(selectors.UserPage.button_to_open_subscriptions_list).click()  # открыть список подписок
        subscriptions_div_block = self.search_element(selectors.UserPage.subscriptions_list_div_block)
        subscriptions_users = subscriptions_div_block.find_elements(selectors.Technical.tag_li)
        return subscriptions_users

    def save_to_file_accounts_followers(self):
        self.search_element(selectors.UserPage.button_to_open_followers_list).click()  # открыть список подписчиков
        self.scrolling_div_block(count=Parce.scroll_number_subscribers_list + 1)
        user_urls = self.search_elements_on_tag(ignore=self.account_option.account_data["user_name"])
        Tools.file_write((BotOption.parameters["non_filtered_path"]), user_urls)
        self.print_statistics_on_parce()
