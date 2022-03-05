from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from module.exception_module import FilterException, StopWordException, BadProfileException
from selenium.webdriver.support import expected_conditions as ec
from module.message_text_module import FilterMessage
from selenium.webdriver.common.by import By
from module.base_module import BaseClass
from settings import Subscribe
import requests
import hashlib


class FilterClass(BaseClass):
    # комплексный фильтр
    def should_be_compliance_with_limits(self):
        self.should_be_profile_avatar()
        self.should_be_private_profile()
        self.should_be_subscribe()
        self.should_be_posts()
        self.check_posts_follows_and_subs_amount()
        self.should_be_stop_word_in_biography()

    # проверяет, подписан ли на пользователя
    def should_be_subscribe(self):
        """
        вернёт False если если подписка уже есть
        """
        try:
            self.search_element((By.CSS_SELECTOR, 'span.vBF20._1OSdk > button > div > span'), timeout=1)
            raise FilterException(FilterMessage.already_subscribe)
        except TimeoutException:
            pass
        #     exist = True
        # return exist

    # проверяет, есть ли публикации в профиле
    def should_be_posts(self):
        try:
            self.search_element((By.XPATH, '//article/div[1]/div/div[2]/h1'), timeout=1)
            raise FilterException(FilterMessage.no_posts)
        except TimeoutException:
            pass
        #     exist = True
        # return exist

    # проверяет, не является ли профиль закрытым
    def should_be_private_profile(self):
        try:
            self.search_element((By.XPATH, '//article/div[1]/div/h2'), timeout=0.5)
            raise FilterException(FilterMessage.profile_closed)
        except TimeoutException:
            pass
        except StaleElementReferenceException:
            print('Проблемы при поиске элемента, пропускаю профиль')
        # return exist

    # проверяет наличие аватара
    def should_be_profile_avatar(self):
        digests = []
        url = self.get_link((By.CSS_SELECTOR, 'div.eC4Dz img'))
        get_img = requests.get(url)
        with open('data/profile_avatar.jpg', 'wb') as img_file:
            img_file.write(get_img.content)
        for filename in ['data/sample.jpg', 'data/profile_avatar.jpg']:
            hasher = hashlib.md5()
            with open(filename, 'rb') as f:
                buf = f.read()
                hasher.update(buf)
                a = hasher.hexdigest()
                digests.append(a)
        if digests[0] == digests[1]:
            raise FilterException(FilterMessage.no_avatar)

    # проверяет наличие стоп-слов в биографии
    def should_be_stop_word_in_biography(self):
        stop_words = Subscribe.stop_word_dict
        try:
            biography = self.search_element((By.CSS_SELECTOR, 'div.QGPIr > span'), timeout=1,
                                            type_wait=ec.presence_of_element_located).text
            for word in stop_words:
                assert word.lower() not in biography.lower()
        except AssertionError:
            raise StopWordException(FilterMessage.stop_word, word)
        except TimeoutException:
            pass

    # сверяет количество постов, подписчиков и подписок с лимитами
    def check_posts_follows_and_subs_amount(self):
        max_coefficient = Subscribe.coefficient_subscribers
        posts_max = Subscribe.posts_max
        posts_min = Subscribe.posts_min
        subscribers_max = Subscribe.subscribers_max
        subscribers_min = Subscribe.subscribers_min
        subscriptions_max = Subscribe.subscriptions_max
        subscriptions_min = Subscribe.subscriptions_min
        break_limit = Subscribe.break_limit
        data_dict = self.return_number_posts_subscribe_and_subscribers()
        coefficient = data_dict['subs'] / data_dict['follow']

        if not posts_max >= data_dict['posts'] >= posts_min:
            raise FilterException(FilterMessage.filter_posts)

        if not subscribers_max >= data_dict['follow'] >= subscribers_min:
            raise FilterException(FilterMessage.filter_follow)

        if not subscriptions_max >= data_dict['subs'] >= subscriptions_min:
            raise FilterException(FilterMessage.filter_subs)

        if data_dict['follow'] < break_limit and coefficient <= max_coefficient:
            raise BadProfileException(FilterMessage.bad_profile)
