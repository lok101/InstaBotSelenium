from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from module.exception import BadProfile, FilteredOut, EmptyProfile, StopWord
from selenium.webdriver.support import expected_conditions as ec
from module.message_text import FilterMessage
from module.base_module import BaseClass
from module import selectors
from settings import Filter
import requests
import hashlib


class FilterClass(BaseClass):
    # комплексный фильтр
    def should_be_compliance_with_limits(self):
        self.should_be_profile_avatar()
        self.should_be_subscribe()
        self.check_posts_follows_and_subs_amount()
        self.should_be_stop_word_in_nick_name()
        self.should_be_stop_word_in_user_name()
        self.should_be_stop_word_in_biography()
        print('Подходит.')

    # проверяет, подписан ли на пользователя
    def should_be_subscribe(self):
        try:
            self.search_element(selectors.UserPage.button_unsubscribe, timeout=1)
            raise FilteredOut(self.account_option, FilterMessage.already_subscribe)
        except TimeoutException:
            pass

    # проверяет, не является ли профиль закрытым
    def should_be_private_profile(self):
        try:
            self.search_element(selectors.UserPage.label_this_close_account, timeout=0.5)
            raise EmptyProfile(self.account_option, FilterMessage.profile_closed)
        except TimeoutException:
            pass
        except StaleElementReferenceException:
            print('Проблемы при поиске элемента, пропускаю профиль')
        # return exist

    # проверяет наличие аватара
    def should_be_profile_avatar(self):
        digests = []
        url = self.get_link(selectors.UserPage.account_photo)
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
            raise EmptyProfile(self.account_option, FilterMessage.no_avatar)

    # проверяет наличие стоп-слов в никнейме
    def should_be_stop_word_in_nick_name(self):
        stop_words = StopWords.stop_word_in_nick_name
        assert_text = FilterMessage.stop_word_in_nick_name
        field = self.account_option.user_url.split("/")[-2]
        self.search_stop_word_in_argument(field, stop_words, assert_text)

    # проверяет наличие стоп-слов в имени
    def should_be_stop_word_in_user_name(self):
        stop_words = StopWords.stop_word_in_user_name
        assert_text = FilterMessage.stop_word_in_user_name
        try:
            field = self.search_element(selectors.UserPage.user_name, timeout=1,
                                        type_wait=ec.presence_of_element_located).text
            self.search_stop_word_in_argument(field, stop_words, assert_text)
        except TimeoutException:
            pass

    # проверяет наличие стоп-слов в биографии
    def should_be_stop_word_in_biography(self):
        stop_words = StopWords.stop_word_in_biography
        assert_text = FilterMessage.stop_word_in_biography
        try:
            field = self.search_element(selectors.UserPage.user_biography, timeout=1,
                                        type_wait=ec.presence_of_element_located).text
            self.search_stop_word_in_argument(field, stop_words, assert_text)
        except TimeoutException:
            pass

    def search_stop_word_in_argument(self, field, stop_words_list, assert_text):
        try:
            for word in stop_words_list:
                assert word.lower() not in field.lower()
        except AssertionError:
            exception_text = f'{assert_text} {word}'
            raise StopWord(self.account_option, exception_text)

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
        data_dict = self.return_amount_posts_subscribes_and_subscribers()
        coefficient = data_dict['subs'] / data_dict['follow']

        if not posts_max >= data_dict['posts'] >= posts_min:
            raise FilteredOut(self.account_option, FilterMessage.filter_posts)

        if not follow_max >= data_dict['follow'] >= follow_min:
            raise FilteredOut(self.account_option, FilterMessage.filter_follow)

        if not subs_max >= data_dict['subs'] >= subs_min:
            raise FilteredOut(self.account_option, FilterMessage.filter_subs)

        if data_dict['follow'] < break_limit and coefficient <= max_coefficient:
            raise BadProfile(self.account_option, FilterMessage.bad_profile)


class StopWords:
    stop_word_in_nick_name = [
        'giv', 'darom', 'salon'
    ]

    stop_word_in_user_name = [
        'á', 'ç', 'ك', 'ا', 'ل', 'س', 'ل', 'ا', 'م', 'Č', 'Š', 'Ě', 'і', 'і', 'ї', 'қ', 'ү', 'Í', 'перманент', 'бров',
        'макияж'
    ]

    stop_word_in_biography = [
        'привет', 'цена', 'цены', 'предоплат', 'доставк', 'отправк', 'изготов', 'психолог', 'кератин', 'ботокс',
        'мастер',
        'специалист', 'директ', 'direct', 'заказ', 'зарабатывать', 'адрес', 'y.o', 'лет', 'товар', 'розыгрыш',
        'юридическ',
        'фирма', 'связи', 'менеджер', 'изделия', 'телефон', 'амбасадор', 'услуг', 'украин', 'холост', 'массаж',
        'магазин',
        'маникюр', 'педикюр', 'информационный', 'портал', 'леденцы', 'запись', 'тел:', 'реклама', 'бесплатно', '8(',
        '7(',
        'дарим', 'оплата', 'коран', 'новости', 'консультант', 'результат', 'под ключ', 'скидк', 'ссылк', 'режим работы',
        'á', 'ç', 'ك', 'ا', 'ل', 'س', 'ل', 'ا', 'م', 'Č', 'Š', 'Ě', 'і', 'і', 'ї', 'қ', 'ү', 'Í', 'акци', 'перманент'
                                                                                                          'формата',
        'сбор', 'волонт', 'бров', 'съёмк', 'киев', 'тел.', '₽'
    ]