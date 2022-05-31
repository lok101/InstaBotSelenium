import random
import time

from settings import Subscribe, Unsubscribe, Parce
from module import exception, message_text, selectors

from module.base_module import BaseClass
from module.filters import Filter
from module.service import Check, Text, Tools, Print


class Support:
    @staticmethod
    def press_to_subscribe_button(bot):
        BaseClass.search_element(bot, selectors.UserPage.all_buttons)  # выполняет роль проверки на загрузку
        buttons = bot.browser.find_elements(*selectors.UserPage.all_buttons)
        for button in buttons:
            if 'подписаться' in button.text.lower():
                iteration_limit = 10
                iteration_count = 0
                while iteration_count < iteration_limit:
                    iteration_count += 1
                    button.click()
                    time.sleep(random.randrange(Subscribe.min_timeout, Subscribe.max_timeout))
                    Check.should_be_subscribe_and_unsubscribe_blocking(bot)
                    Tools.file_write(
                        (BaseClass.parameters["ignore_list_path"]),
                        bot.account_data['account_url']
                    )
                    bot.count_iteration += 1
                    Print.to_console(
                        Text(bot).subscribe_successful()
                    )
                    return
        Print.to_console(
            Text(bot).button_not_found()
        )
        Tools.file_write(
            (BaseClass.parameters["ignore_list_path"]),
            bot.account_data['account_url']
        )
        time.sleep(random.randrange(Subscribe.min_timeout, Subscribe.max_timeout))

    @staticmethod
    def check_limits_from_subscribe(bot):
        if bot.count_iteration % Subscribe.subscribe_in_session == 0 and bot.count_iteration != 0:
            Support.go_to_my_profile_page_and_set_subscribes_amount(bot)
            Print.to_console(
                Text(bot).current_time(),
                Text(bot).account_name(),
                Text(bot).subscribe_limit_info()
            )
            time.sleep(Subscribe.sleep_between_iterations * 60)

    @staticmethod
    def press_to_unsubscribe_button_and_set_timeouts(bot, user):
        user.find_element(*selectors.UserPage.all_buttons).click()  # нажать кнопку отписки
        time.sleep(random.randrange(Unsubscribe.min_sleep, Unsubscribe.max_sleep))
        BaseClass.search_element(bot,
                                 selectors.UserPage.button_confirm_unsubscribe).click()  # нажать кнопку подтверждения
        Check.should_be_subscribe_and_unsubscribe_blocking(bot)
        bot.count_iteration += 1
        Print.to_console(
            Text(bot).current_time(),
            Text(bot).account_name(),
            Text(bot).unsubscribe_click_info()
        )

    @staticmethod
    def go_to_user_page(bot):
        bot.browser.get(bot.account_data['account_url'])
        Print.to_console(
            Text(bot).current_time(),
            Text(bot).account_name(),
            Text(bot).profile_page_info()
        )

        Check.should_be_instagram_page(bot)
        Check.should_be_verification_forms(bot)
        Check.should_be_user_page(bot)
        Check.should_be_activity_blocking(bot)
        Check.check_cookie_accept_window(bot)

    @staticmethod
    def go_to_my_profile_page_and_set_subscribes_amount(bot):
        url = f'https://www.instagram.com/{bot.account_data["user_name"]}/'
        bot.browser.get(url)
        Check.should_be_instagram_page(bot)
        Check.should_be_activity_blocking(bot)
        Check.should_be_verification_forms(bot)

        bot.subscribes = Filter.return_amount_posts_subscribes_and_subscribers(bot)['subs']
        Print.to_console(
            Text(bot).current_time(),
            Text(bot).account_name(),
            Text(bot).subscribe_amount()
        )

    @staticmethod
    def get_users_url_for_parce(bot):
        urls_public = []
        Tools.file_read((BaseClass.parameters["parce_url_path"]), urls_public)
        bot.count_limit = len(urls_public)
        if bot.count_iteration + 1 >= bot.count_limit:
            raise exception.BotFinishTask(
                bot, message_text.InformationMessage.task_finish)
        urls_public = urls_public[bot.count_iteration:-1]
        return urls_public

    @staticmethod
    def go_timer(bot):
        if bot.account_data["timer"] != 0:
            Print.to_console(
                Text(bot).current_time(),
                Text(bot).account_name(),
                Text(bot).print_timer()
            )
            time.sleep(int(bot.account_data["timer"]) * 60)

    @staticmethod
    def shaffle_file_for_task(bot):
        if bot.account_data["WORK_MODE"] == BaseClass.parameters['par']:
            Tools.shaffle_file(BaseClass.parameters['parce_url_path'])
            Print.to_console(
                Text(bot).current_time(),
                Text(bot).account_name(),
                Text(bot).shuffle_parce_file()
            )
        elif bot.account_data["WORK_MODE"] == BaseClass.parameters['fil']:
            Tools.shaffle_file(BaseClass.parameters['non_filtered_path'])
            Print.to_console(
                Text(bot).current_time(),
                Text(bot).account_name(),
                Text(bot).shuffle_filter_file()
            )
        else:
            raise Exception('Неизвестный режим в методе "shaffle_file_for_task".')

    @staticmethod
    def return_subscriptions_list_for_this_account(bot):
        BaseClass.search_element(bot,
                                 selectors.UserPage.button_to_open_subscriptions_list).click()  # открыть список подписок
        subscriptions_div_block = BaseClass.search_element(bot, selectors.UserPage.subscriptions_list_div_block)
        subscriptions_users = subscriptions_div_block.find_elements(*selectors.Technical.tag_li)
        return subscriptions_users

    @staticmethod
    def save_to_file_accounts_followers(bot):
        BaseClass.search_element(bot, selectors.UserPage.button_to_open_followers_list).click()  # открыть подписчиков
        BaseClass.scrolling_div_block(bot, count=Parce.scroll_number_subscribers_list + 1)
        user_urls = BaseClass.search_elements_on_tag(bot, ignore=bot.account_data["user_name"])
        Tools.file_write((BaseClass.parameters["non_filtered_path"]), user_urls)
        Text(bot).print_statistics_on_parce()
