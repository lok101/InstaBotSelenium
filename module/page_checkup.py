from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from module import base_module, exception, message_text
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import time


class Checks(base_module.BaseClass):
    def should_be_user_page(self):
        while True:
            try:
                error_message = self.search_element((By.CSS_SELECTOR, 'div > div > h2'), timeout=1,
                                                    type_wait=ec.presence_of_element_located)
                if 'К сожалению, эта страница недоступна' in error_message.text:
                    raise exception_module.UserPageNotExist(
                        self.account_option,
                        message_text_module.InformationMessage.page_not_exist)
                elif 'Это закрытый аккаунт' in error_message.text:
                    raise exception_module.PageNotAvailable(
                        self.account_option,
                        message_text_module.FilterMessage.profile_closed)
                elif 'Вам исполнилось' in error_message.text:
                    raise exception_module.PageNotAvailable(
                        self.account_option,
                        message_text_module.InformationMessage.check_age)
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
            print(f'Логин с аккаунта - {self.account_option.username}')
        except TimeoutException:
            raise exception_module.LoginError(
                self.account_option,
                message_text_module.LoginErrorMessage.not_login_page)

    def should_be_verification_form(self):
        try:
            self.search_element((By.CSS_SELECTOR, 'div.ctQZg.KtFt3 > button > div'), timeout=2)
            raise exception_module.VerificationError(
                self.account_option,
                message_text_module.LoginErrorMessage.verification_form)

        except TimeoutException:
            pass

    def should_be_login_form_error(self):
        try:
            element = self.search_element((By.CSS_SELECTOR, '#slfErrorAlert'),
                                          timeout=10, type_wait=ec.presence_of_element_located)
            if 'К сожалению, вы ввели неправильный пароль.' in element.text:
                raise exception_module.LoginError(
                    self.account_option,
                    message_text_module.LoginErrorMessage.error_pass)
            if 'не принадлежит аккаунту' in element.text:
                raise exception_module.LoginError(
                    self.account_option,
                    message_text_module.LoginErrorMessage.error_account_name)
            raise exception_module.LoginError(
                self.account_option,
                message_text_module.LoginErrorMessage.login_form_error)
        except TimeoutException:
            pass

    def should_be_login_button(self, mode='login-pass'):
        try:
            self.search_element((By.CSS_SELECTOR, 'div.ctQZg.KtFt3 > div > div:nth-child(1)'), timeout=2,
                                type_wait=ec.presence_of_element_located)

        except TimeoutException:
            if mode == 'cookie':
                message = message_text_module.LoginErrorMessage.broke_cookie
            else:
                message = message_text_module.LoginErrorMessage.not_login
            raise exception_module.LoginError(self.account_option, message)

    def should_be_subscribe_and_unsubscribe_blocking(self):
        try:
            self.search_element((By.CSS_SELECTOR, 'div._08v79 > h3'), timeout=2,
                                type_wait=ec.presence_of_element_located)
            raise exception_module.ActivBlocking(
                self.account_option,
                message_text_module.InformationMessage.subscribe_unsubscribe_blocking)

        except TimeoutException:
            pass

    def should_be_activity_blocking(self):
        try:
            error_message = self.search_element((By.CSS_SELECTOR, 'div > div.error-container > p'), timeout=2,
                                                type_wait=ec.presence_of_element_located)
            if 'Подождите несколько минут, прежде чем пытаться снова' in error_message.text:
                raise exception_module.ActivBlocking(
                    self.account_option,
                    message_text_module.InformationMessage.activiti_blocking)
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
            raise exception_module.PageLoadingError(
                self.account_option,
                message_text_module.InformationMessage.page_loading_error)

    def cookie_accept(self):
        accept_button = self.search_element((By.CSS_SELECTOR, 'button.aOOlW.HoLwm'))
        accept_button.click()
        time.sleep(2)