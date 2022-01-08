from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as ec
from module.base_module import BaseClass, download_for_link
from selenium.webdriver.common.by import By
import hashlib


class FilterClass(BaseClass):
    # проверяет, стоит ли лайк
    def should_be_like(self):
        try:
            self.search_element((By.CSS_SELECTOR, 'span.fr66n > button > div.QBdPU.B58H7 > svg'), timeout=1)
            exist = True
        except TimeoutException:
            exist = False
        return exist

    # проверяет, подписан ли на пользователя
    def should_be_subscribe(self):
        """
        вернёт False если если подписка уже есть
        """
        try:
            self.search_element((By.CSS_SELECTOR, 'span.vBF20._1OSdk > button > div > span'), timeout=1)
            exist = False
        except TimeoutException:
            exist = True
        return exist

    # проверяет, есть ли публикации в профиле
    def should_be_posts(self):
        """
        вернёт False если найдёт надпись "Публикаций пока нет"
        """
        try:
            self.search_element((By.XPATH, '//article/div[1]/div/div[2]/h1'), timeout=1)
            exist = False
        except TimeoutException:
            exist = True
        return exist

    # комплексный фильтр подписки/подписчики/посты
    def should_be_compliance_with_limits(self, max_coefficient, posts_max, posts_min, subscribers_max, subscribers_min,
                                         subscriptions_max, subscriptions_min):
        # assert-функции, вывод которых прописан КАПСОМ - пишутся в лог файл
        number_posts_subscribe_and_subscribers = self.return_number_posts_subscribe_and_subscribers()
        posts_number = number_posts_subscribe_and_subscribers[1]
        subscribers_count = number_posts_subscribe_and_subscribers[2]
        subscriptions_count = number_posts_subscribe_and_subscribers[3]
        coefficient = number_posts_subscribe_and_subscribers[0]
        assert posts_max >= posts_number >= posts_min, 'Не прошёл по постам.'
        assert subscribers_max >= subscribers_count >= subscribers_min, 'Не прошёл по подписчикам.'
        assert subscriptions_max >= subscriptions_count >= subscriptions_min, 'Не прошёл по подпискам.'
        assert coefficient <= max_coefficient, 'ПРОФИЛЬ "ПОМОЙКА".'

    # проверяет, не является ли профиль закрытым
    def should_be_privat_profile(self):
        """
        вернёт False если профиль закрыт
        """
        try:
            self.search_element((By.XPATH, '//article/div[1]/div/h2'), timeout=1)
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
        download_for_link(url)  # качает изображение и кладёт его в 'data/profile_avatar.jpg'
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
        return [flag, word]

    # возвращает колличество постов, подписчиков, подписок и коэффицент подписки/подписчики
    def return_number_posts_subscribe_and_subscribers(self):
        try:
            subscribers_field = self.search_element((By.CSS_SELECTOR, 'li:nth-child(3) > a > span'),
                                                    type_wait=ec.presence_of_element_located, timeout=3)

            subscriptions = int(
                subscribers_field.text.replace(" ", "").replace(',', ''))
        except TimeoutException:
            subscriptions = 0

        subscribe_field = self.search_element((By.CSS_SELECTOR, 'li:nth-child(2) > a > span'),
                                              type_wait=ec.presence_of_element_located)
        if ',' in subscribe_field.text:
            subscribers = int(
                subscribe_field.text.replace(" ", "").replace(',', '').replace('тыс.', '00').replace('млн', '00000'))
        else:
            subscribers = int(
                subscribe_field.text.replace(" ", "").replace('тыс.', '000').replace('млн', '000000'))

        post_number_field = self.search_element((By.CSS_SELECTOR, 'li:nth-child(1) > span > span'),
                                                type_wait=ec.presence_of_element_located)
        posts_number = int(
            post_number_field.text.replace(" ", "").replace(',', '').replace('тыс.', '000').replace('млн', '000000'))

        return [subscriptions / subscribers, posts_number, subscribers, subscriptions]
