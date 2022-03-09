from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from module.exception_module import FilteredOut, StopWord, BadProfile, EmptyProfile
from selenium.webdriver.support import expected_conditions as ec
from module.message_text_module import FilterMessage
from selenium.webdriver.common.by import By
from module.base_module import BaseClass
from settings import Filter
import requests
import hashlib


class FilterClass(BaseClass):
    # комплексный фильтр
    def should_be_compliance_with_limits(self):
        self.should_be_profile_avatar()
        self.should_be_subscribe()
        self.should_be_posts()
        self.check_posts_follows_and_subs_amount()
        self.should_be_stop_word_in_nick_name()
        self.should_be_stop_word_in_user_name()
        self.should_be_stop_word_in_biography()
        print('Подходит.')

    # проверяет, подписан ли на пользователя
    def should_be_subscribe(self):
        """
        вернёт False если если подписка уже есть
        """
        try:
            self.search_element((By.CSS_SELECTOR, 'span.vBF20._1OSdk > button > div > span'), timeout=1)
            raise FilteredOut(FilterMessage.already_subscribe)
        except TimeoutException:
            pass

    # проверяет, есть ли публикации в профиле
    def should_be_posts(self):
        try:
            self.search_element((By.XPATH, '//article/div[1]/div/div[2]/h1'), timeout=1)
            raise EmptyProfile(FilterMessage.no_posts)
        except TimeoutException:
            pass

    # проверяет, не является ли профиль закрытым
    def should_be_private_profile(self):
        try:
            self.search_element((By.XPATH, '//article/div[1]/div/h2'), timeout=0.5)
            raise EmptyProfile(FilterMessage.profile_closed)
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
            raise EmptyProfile(FilterMessage.no_avatar)

    # проверяет наличие стоп-слов в никнейме
    def should_be_stop_word_in_nick_name(self):
        stop_words = Filter.stop_word_in_nick_name_list
        assert_text = FilterMessage.stop_word_in_nick_name
        field = self.user_url.split("/")[-2]
        self.search_stop_word_in_argument(field, stop_words, assert_text)

    # проверяет наличие стоп-слов в имени
    def should_be_stop_word_in_user_name(self):
        stop_words = Filter.stop_word_in_user_name_list
        assert_text = FilterMessage.stop_word_in_user_name
        try:
            field = self.search_element((By.CSS_SELECTOR, 'div.QGPIr > span'), timeout=1,
                                        type_wait=ec.presence_of_element_located).text
            self.search_stop_word_in_argument(field, stop_words, assert_text)
        except TimeoutException:
            pass

    # проверяет наличие стоп-слов в биографии
    def should_be_stop_word_in_biography(self):
        stop_words = Filter.stop_word_in_biography_list
        assert_text = FilterMessage.stop_word_in_biography
        try:
            field = self.search_element((By.CSS_SELECTOR, 'div.QGPIr > div'), timeout=1,
                                        type_wait=ec.presence_of_element_located).text
            self.search_stop_word_in_argument(field, stop_words, assert_text)
        except TimeoutException:
            pass

    @staticmethod
    def search_stop_word_in_argument(field, stop_words_list, assert_text):
        try:
            for word in stop_words_list:
                assert word.lower() not in field.lower()
        except AssertionError:
            raise StopWord(assert_text, word)

    # сверяет количество постов, подписчиков и подписок с лимитами
    def check_posts_follows_and_subs_amount(self):
        max_coefficient = Filter.coefficient_subscribers
        posts_max = Filter.posts_max
        posts_min = Filter.posts_min
        follow_max = Filter.follow_max
        follow_min = Filter.follow_min
        subs_max = Filter.subs_max
        subs_min = Filter.subs_min
        break_limit = Filter.break_limit
        data_dict = self.return_number_posts_subscribe_and_subscribers()
        coefficient = data_dict['subs'] / data_dict['follow']

        if not posts_max >= data_dict['posts'] >= posts_min:
            raise FilteredOut(FilterMessage.filter_posts)

        if not follow_max >= data_dict['follow'] >= follow_min:
            raise FilteredOut(FilterMessage.filter_follow)

        if not subs_max >= data_dict['subs'] >= subs_min:
            raise FilteredOut(FilterMessage.filter_subs)

        if data_dict['follow'] < break_limit and coefficient <= max_coefficient:
            raise BadProfile(FilterMessage.bad_profile)
