from selenium import webdriver

import pickle
import time

from module import selectors
from module.base_module import BaseClass
from module.service import Check, Text, Print


class Login:
    @staticmethod
    def cookie_login(bot):
        bot.browser = webdriver.Chrome(options=bot.account_data['chrome_option'])
        bot.browser.get('https://www.instagram.com/accounts/login/')
        Login.set_cookie(bot)
        Check.should_be_verification_forms(bot)
        Check.should_be_login_button(bot)
        Print.to_console(
            Text(bot).current_time(),
            Text(bot).account_name(),
            Text(bot).login_from_cookie()
        )

    @staticmethod
    def not_cookie_login(bot):
        BaseClass.input_username_and_userpass(bot)
        Check.should_be_login_form_error(bot)
        Check.should_be_verification_forms(bot)
        Check.should_be_login_button(bot)
        Login.save_new_cookie(bot)
        Print.to_console(
            Text(bot).current_time(),
            Text(bot).account_name(),
            Text(bot).login_not_cookie()
        )

    @staticmethod
    def check_proxy_ip(bot):
        bot.browser.get('https://api.myip.com/')
        BaseClass.compare_my_ip_and_base_ip(bot)
        Print.to_console(
            Text(bot).current_time(),
            Text(bot).account_name(),
            Text(bot).proxy_successful_connection()
        )

    @staticmethod
    def set_cookie(bot):
        bot.browser.delete_all_cookies()
        bot.browser.refresh()
        button_cookie_accept = BaseClass.search_element(bot, selectors.Login.button_cookie_accept)
        button_cookie_accept.click()
        time.sleep(2)
        Check.should_be_login_page(bot)
        for cookie in pickle.load(
                open(f'data/cookies_and_userAgent/{bot.account_data["user_name"]}_cookies', 'rb')):
            bot.browser.add_cookie(cookie)
        time.sleep(1)
        bot.browser.refresh()

    @staticmethod
    def save_new_cookie(bot):
        pickle.dump(bot.browser.get_cookies(),
                    open(f'data/cookies_and_userAgent/{bot.account_data["user_name"]}_cookies', 'wb'))
