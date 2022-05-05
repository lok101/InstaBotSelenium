from module import exception, message_text, page_checkup
from selenium.webdriver.common.by import By
import random
import time

from module.option import BotOption
from module.tools import Tools
from settings import Subscribe, Unsubscribe


class Navigation(page_checkup.Checks):
    def press_to_subscribe_button(self):
        self.search_element((By.CSS_SELECTOR, 'div button'))  # выполняет роль проверки на загрузку
        buttons = self.browser.find_elements(By.CSS_SELECTOR, 'div button')
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
                    print('Успешно подписался.')
                    return
        print('Кнопка не найдена.')
        Tools.file_write((BotOption.parameters["ignore_list_path"]), self.account_option.user_url)
        time.sleep(random.randrange(Subscribe.min_timeout, Subscribe.max_timeout))

    def check_limits_from_subscribe(self):
        if self.count_iteration % Subscribe.subscribe_in_session == 0 and self.count_iteration != 0:
            self.go_to_my_profile_page_and_set_subscribes_amount()
            self.print_to_console_current_time_and_account_name(
                self.print_subscribe_limit_info)
            time.sleep(Subscribe.sleep_between_iterations * 60)

    def press_to_unsubscribe_button_and_set_timeouts(self, user):
        user.find_element(By.TAG_NAME, "button").click()  # нажать кнопку отписки
        time.sleep(random.randrange(Unsubscribe.min_sleep, Unsubscribe.max_sleep))
        self.search_element((By.CSS_SELECTOR, "button.-Cab_")).click()  # нажать кнопку подтверждения
        self.should_be_subscribe_and_unsubscribe_blocking()
        self.count_iteration += 1
        self.print_to_console_current_time_and_account_name(
            self.print_unsubscribe_click_info)

    def go_to_user_page(self):
        self.browser.get(self.account_option.user_url)
        self.print_to_console_current_time_and_account_name(
            self.print_profile_page_info)

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
        self.print_to_console_current_time_and_account_name(
            self.print_subscribe_amount)

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
            self.print_to_console_current_time_and_account_name(
                self.print_timer)
            time.sleep(int(self.account_option.timer) * 60)
