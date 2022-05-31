from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as ec

import requests
import hashlib

from module.exception import BadProfile, FilteredOut, EmptyProfile, StopWord
from module.message_text import FilterMessage
from settings import FilterLimits
from module import selectors

from module.base_module import BaseClass


class Filter:
    @staticmethod
    def should_be_compliance_with_limits(bot):
        Filter.should_be_profile_avatar(bot)
        Filter.should_be_subscribe(bot)
        Filter.check_posts_follows_and_subs_amount(bot)
        Filter.should_be_stop_word_in_nick_name(bot)
        Filter.should_be_stop_word_in_user_name(bot)
        Filter.should_be_stop_word_in_biography(bot)
        print('Подходит.')

    # проверяет, подписан ли на пользователя
    @staticmethod
    def should_be_subscribe(bot):
        try:
            BaseClass.search_element(bot, selectors.UserPage.all_buttons)  # выполняет роль проверки на загрузку
            buttons = bot.browser.find_elements(*selectors.UserPage.all_buttons)
            for button in buttons[:10]:
                if 'подписаться' in button.text.lower():
                    return
            raise FilteredOut(bot, FilterMessage.already_subscribe)
        except TimeoutException:
            pass

    # проверяет, не является ли профиль закрытым
    @staticmethod
    def should_be_private_profile(bot):
        try:
            BaseClass.search_element(bot, selectors.UserPage.label_this_close_account, timeout=0.5)
            raise EmptyProfile(bot, FilterMessage.profile_closed)
        except TimeoutException:
            pass
        except StaleElementReferenceException:
            print('Проблемы при поиске элемента, пропускаю профиль')
        # return exist

    # проверяет наличие аватара
    @staticmethod
    def should_be_profile_avatar(bot):
        digests = []
        url = BaseClass.get_link(bot, selectors.UserPage.account_photo)
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
            raise EmptyProfile(bot, FilterMessage.no_avatar)

    # проверяет наличие стоп-слов в никнейме
    @staticmethod
    def should_be_stop_word_in_nick_name(bot):
        stop_words = StopWords.stop_word_in_nick_name
        assert_text = FilterMessage.stop_word_in_nick_name
        field = bot.account_data['account_url'].split("/")[-2]
        Filter.search_stop_word_in_argument(bot, field, stop_words, assert_text)

    # проверяет наличие стоп-слов в имени
    @staticmethod
    def should_be_stop_word_in_user_name(bot):
        stop_words = StopWords.stop_word_in_user_name
        assert_text = FilterMessage.stop_word_in_user_name
        try:
            field = BaseClass.search_element(
                bot, selectors.UserPage.user_name,
                type_wait=ec.presence_of_element_located,
                timeout=1,
            ).text
            Filter.search_stop_word_in_argument(bot, field, stop_words, assert_text)
        except TimeoutException:
            pass

    # проверяет наличие стоп-слов в биографии
    @staticmethod
    def should_be_stop_word_in_biography(bot):
        stop_words = StopWords.stop_word_in_biography
        assert_text = FilterMessage.stop_word_in_biography
        try:
            field = BaseClass.search_element(
                bot, selectors.UserPage.user_biography,
                type_wait=ec.presence_of_element_located,
                timeout=1,
            ).text
            Filter.search_stop_word_in_argument(bot, field, stop_words, assert_text)
        except TimeoutException:
            pass

    @staticmethod
    def search_stop_word_in_argument(bot, field, stop_words_list, assert_text):
        try:
            for word in stop_words_list:
                assert word.lower() not in field.lower()
        except AssertionError:
            exception_text = f'{assert_text} {word}'
            raise StopWord(bot, exception_text)

    # сверяет количество постов, подписчиков и подписок с лимитами
    @staticmethod
    def check_posts_follows_and_subs_amount(bot):
        max_coefficient = FilterLimits.coefficient_subscribers
        posts_max = FilterLimits.posts_max
        posts_min = FilterLimits.posts_min
        follow_max = FilterLimits.follow_max
        follow_min = FilterLimits.follow_min
        subs_max = FilterLimits.subs_max
        subs_min = FilterLimits.subs_min
        break_limit = FilterLimits.break_limit
        data_dict = Filter.return_amount_posts_subscribes_and_subscribers(bot)
        coefficient = data_dict['subs'] / data_dict['follow']

        if not posts_max >= data_dict['posts'] >= posts_min:
            raise FilteredOut(bot, FilterMessage.filter_posts)

        if not follow_max >= data_dict['follow'] >= follow_min:
            raise FilteredOut(bot, FilterMessage.filter_follow)

        if not subs_max >= data_dict['subs'] >= subs_min:
            raise FilteredOut(bot, FilterMessage.filter_subs)

        if data_dict['follow'] < break_limit and coefficient <= max_coefficient:
            raise BadProfile(bot, FilterMessage.bad_profile)

    @staticmethod
    def return_amount_posts_subscribes_and_subscribers(bot):
        dict_return = dict()
        try:
            subscriptions_field = BaseClass.search_element(
                bot, selectors.UserPage.subscriptions,
                type_wait=ec.presence_of_element_located,
                timeout=3
            )
            dict_return['subs'] = int(
                subscriptions_field.text.replace(" ", "").replace(',', ''))
        except TimeoutException:
            dict_return['subs'] = 0

        try:
            followers_field = BaseClass.search_element(
                bot, selectors.UserPage.followers,
                type_wait=ec.presence_of_element_located,
                timeout=3
            )
            if ',' in followers_field.text:
                dict_return['follow'] = int(followers_field.text.lower().
                                            replace(" ", "").
                                            replace(',', '').
                                            replace('тыс.', '00').
                                            replace('млн', '00000'))
            else:
                dict_return['follow'] = int(followers_field.text.lower().
                                            replace(" ", "").
                                            replace('тыс.', '000').
                                            replace('млн', '000000'))
        except TimeoutException:
            dict_return['follow'] = 1

        post_number_field = BaseClass.search_element(
            bot, selectors.UserPage.posts,
            type_wait=ec.presence_of_element_located
        )
        dict_return['posts'] = int(
            post_number_field.text.replace(" ", "").replace(',', '').replace('тыс.', '000').replace('млн', '000000'))

        return dict_return


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
