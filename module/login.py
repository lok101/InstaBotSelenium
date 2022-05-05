from module import page_checkup
from selenium import webdriver


class Login(page_checkup.Checks):
    def cookie_login(self):
        self.browser = webdriver.Chrome(options=self.account_option.chrome_options)
        self.browser.get('https://www.instagram.com/accounts/login/')
        self.set_cookie()
        self.should_be_verification_form()
        self.should_be_login_button()
        self.print_to_console_current_time_and_account_name(
            self.print_login_from_cookie)

    def not_cookie_login(self):
        self.input_username_and_userpass()
        self.should_be_login_form_error()
        self.should_be_verification_form()
        self.should_be_login_button()
        self.save_new_cookie()
        self.print_to_console_current_time_and_account_name(
            self.print_login_not_cookie)

    def check_proxy_ip(self):
        self.browser.get('https://api.myip.com/')
        self.compare_my_ip_and_base_ip()
        self.print_to_console_current_time_and_account_name(
            self.print_proxy_successful_connection)
