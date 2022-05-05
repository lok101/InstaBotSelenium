from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from module import exception, message_text, my_print
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import time


class Checks(my_print.Print):
    def should_be_user_page(self):
        while True:
            try:
                error_message = self.search_element((By.CSS_SELECTOR, 'div > div > h2'), timeout=1,
                                                    type_wait=ec.presence_of_element_located)
                if 'К сожалению, эта страница недоступна' in error_message.text:
                    raise exception.UserPageNotExist(
                        self.account_option,
                        message_text.InformationMessage.page_not_exist)
                elif 'Это закрытый аккаунт' in error_message.text:
                    raise exception.PageNotAvailable(
                        self.account_option,
                        message_text.FilterMessage.profile_closed)
                elif 'Вам исполнилось' in error_message.text:
                    raise exception.PageNotAvailable(
                        self.account_option,
                        message_text.InformationMessage.check_age)
                else:
                    print('Неизвестное окно при вызове "should_be_user_page".')
                break

            except TimeoutException:
                break

            except StaleElementReferenceException:
                continue

    def should_be_home_page(self):
        try:
            self.search_element((By.NAME, "username"),
                                timeout=10, type_wait=ec.presence_of_element_located)
            self.print_to_console_current_time_and_account_name(
                self.print_start_login)
        except TimeoutException:
            raise exception.LoginError(
                self.account_option,
                message_text.LoginErrorMessage.not_login_page)

    def should_be_verification_form(self):
        try:
            self.search_element((By.CSS_SELECTOR, 'div.ctQZg.KtFt3 > button > div'), timeout=2)
            raise exception.VerificationError(
                self.account_option,
                message_text.LoginErrorMessage.verification_form)

        except TimeoutException:
            pass

    def should_be_login_form_error(self):
        try:
            element = self.search_element((By.CSS_SELECTOR, '#slfErrorAlert'),
                                          timeout=10, type_wait=ec.presence_of_element_located)
            if 'К сожалению, вы ввели неправильный пароль.' in element.text:
                raise exception.LoginError(
                    self.account_option,
                    message_text.LoginErrorMessage.error_pass)
            if 'не принадлежит аккаунту' in element.text:
                raise exception.LoginError(
                    self.account_option,
                    message_text.LoginErrorMessage.error_account_name)
            raise exception.LoginError(
                self.account_option,
                message_text.LoginErrorMessage.login_form_error)
        except TimeoutException:
            pass

    def should_be_login_button(self, mode='login-pass'):
        try:
            self.search_element((By.CSS_SELECTOR, 'div.ctQZg.KtFt3 > div > div:nth-child(1)'), timeout=2,
                                type_wait=ec.presence_of_element_located)

        except TimeoutException:
            if mode == 'cookie':
                message = message_text.LoginErrorMessage.broke_cookie
            else:
                message = message_text.LoginErrorMessage.not_login
            raise exception.LoginError(self.account_option, message)

    def should_be_subscribe_and_unsubscribe_blocking(self):
        try:
            self.search_element((By.CSS_SELECTOR, 'div._08v79 > h3'), timeout=2,
                                type_wait=ec.presence_of_element_located)
            raise exception.ActivBlocking(
                self.account_option,
                message_text.InformationMessage.subscribe_unsubscribe_blocking)

        except TimeoutException:
            pass

    def should_be_activity_blocking(self):
        try:
            error_message = self.search_element((By.CSS_SELECTOR, 'div > div.error-container > p'), timeout=2,
                                                type_wait=ec.presence_of_element_located)
            if 'Подождите несколько минут, прежде чем пытаться снова' in error_message.text:
                raise exception.ActivBlocking(
                    self.account_option,
                    message_text.InformationMessage.activiti_blocking)
            elif 'cookie' in error_message.text:
                self.cookie_accept()
            else:
                print('Неизвестное всплывающее окно при вызове "should_be_activity_blocking".')
        except TimeoutException:
            pass

    def should_be_instagram_page(self):
        try:
            self.search_element((By.CSS_SELECTOR, '[href=\'/\']'), timeout=15,
                                type_wait=ec.presence_of_element_located)

        except TimeoutException:
            raise exception.PageLoadingError(
                self.account_option,
                message_text.InformationMessage.page_loading_error)

    def cookie_accept(self):
        accept_button = self.search_element((By.CSS_SELECTOR, 'button.aOOlW.HoLwm'))
        accept_button.click()
        time.sleep(2)
