from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from module.message_text_module import FilterMessage
from selenium.webdriver.support import expected_conditions as ec
from module.base_module import BaseClass
from selenium.webdriver.common.by import By
import hashlib


class FilterClass(BaseClass):
    # комплексный фильтр
    def should_be_compliance_with_limits(self, max_coefficient, posts_max, posts_min, subscribers_max, subscribers_min,
                                         subscriptions_max, subscriptions_min, break_limit):
        # assert-функции, вывод которых прописан КАПСОМ - пишутся в лог файл
        assert self.should_be_profile_avatar(), FilterMessage.no_avatar
        assert self.should_be_private_profile(), FilterMessage.profile_closed
        assert self.should_be_subscribe(), FilterMessage.already_subscribe
        assert self.should_be_posts(), FilterMessage.no_posts
        data_dict = self.return_number_posts_subscribe_and_subscribers()
        coefficient = data_dict['subs'] / data_dict['follow']
        assert posts_max >= data_dict['posts'] >= posts_min, FilterMessage.filter_posts
        assert subscribers_max >= data_dict['follow'] >= subscribers_min, FilterMessage.filter_follow
        assert subscriptions_max >= data_dict['subs'] >= subscriptions_min, FilterMessage.filter_subs
        if data_dict['follow'] < break_limit:
            assert coefficient <= max_coefficient, FilterMessage.bad_profile

    # проверяет, подписан ли на пользователя
    def should_be_subscribe(self):
        """
        вернёт False если если подписка уже есть
        """
        try:
            self.search_element((By.CSS_SELECTOR, 'span.vBF20._1OSdk > button > div > span'), timeout=0.5)
            exist = False
        except TimeoutException:
            exist = True
        return exist

    # проверяет, есть ли публикации в профиле
    def should_be_posts(self):
        try:
            self.search_element((By.XPATH, '//article/div[1]/div/div[2]/h1'), timeout=0.5)
            exist = False
        except TimeoutException:
            exist = True
        return exist

    # проверяет, не является ли профиль закрытым
    def should_be_private_profile(self):
        try:
            self.search_element((By.XPATH, '//article/div[1]/div/h2'), timeout=0.5)
            exist = False
        except TimeoutException:
            exist = True
        except StaleElementReferenceException:
            print('Проблемы при поиске элемента, пропускаю профиль')
            exist = False
        return exist

    # проверяет наличие аватара
    def should_be_profile_avatar(self):
        digests = []
        url = self.get_link((By.CSS_SELECTOR, 'div.RR-M- span img._6q-tv'))
        self.download_for_link(url)  # качает изображение и кладёт его в 'data/profile_avatar.jpg'
        for filename in ['data/sample.jpg', 'data/profile_avatar.jpg']:
            hasher = hashlib.md5()
            with open(filename, 'rb') as f:
                buf = f.read()
                hasher.update(buf)
                a = hasher.hexdigest()
                digests.append(a)
        if digests[0] == digests[1]:
            exist = False
        else:
            exist = True
        return exist

    # проверяет наличие стоп-слов в биографии
    def should_be_stop_word_in_biography(self, stop_words):
        word = 'Стоп-слово не присвоено на этапе функции.'
        try:
            biography = self.search_element((By.CSS_SELECTOR, 'div.QGPIr > span'), timeout=1,
                                            type_wait=ec.presence_of_element_located).text
            for word in stop_words:
                assert word.lower() not in biography.lower()
            flag = True
        except TimeoutException:
            flag = True
        except AssertionError:
            flag = False
        return [flag, word.lower()]
