from selenium.webdriver.support import expected_conditions as ec
from data import stop_word_dict


class StartSettings:
    """
    Описывает основные настрйки запуска.
    headless - режим "без головы" (окно браузера не запускается)
    proxy - использовать прокси или нет (сам прокси прописан в data.txt)
    implicitly_wait_timeout - сколько ждать появления элемента во всех этапах, кроме assert-функций
    """
    headless = 'yes'
    proxy = 'yes'
    web_driver_wait = 30
    web_driver_wait_type = ec.element_to_be_clickable


class Unsubscribe:
    """
    Описывает настройки, связанные с отпиской.
    min_sleep - минимальная задержка при отписке (секунды).
    max_sleep - максимальная задержка при отписке (секунды).
    sleep_between_iterations - задержка между итерациями (секунды).
    """
    min_sleep = 5
    max_sleep = 11
    sleep_between_iterations = 150


class Subscribe:
    """
    Описывает настройки, связанные с подпиской.
    timeout - среднее время на одну подписку
    scatter_timeout - разброс при вычислении таймаута
    subscribe_in_session - колличество подписок в одном заходе
    sleep_between_iterations - таймаут на каждые subscribe_in_session подписок
    operating_mode - режим работы (меняет источник сбора аудитории)

    FILTER
    limit_subscribes_min, limit_subscribes_max - максимальное и минимальное число подписчиков для профиля
    limit_posts_min, limit_posts_max - максимальное и минимальное число постов для профиля
    coefficient_subscribers - подписки делённые на подписчиков (если подписок много, а подписчиков мало - пропуск)
    subscribe_limit - колличество подписок в задаче

    """
    operating_mode = 3

    timeout = 2
    scatter_timeout = 1
    subscribe_in_session = 40
    sleep_between_iterations = 20
    subscribe_limit_stop = 400
    """FILTER"""
    subscribers_min, subscribers_max = 50, 5000
    subscriptions_min, subscriptions_max = 50, 6000
    posts_min, posts_max = 3, 800
    coefficient_subscribers = 6
    min_subscribers = 60
    min_subscriptions = 60
    stop_word_dict = stop_word_dict


class SelectUser:
    delete_file = 'no'


class Like:
    min_sleep = 10
    max_sleep = 30


class ErrorLimit:
    error_limit_unsubscribe = 5
