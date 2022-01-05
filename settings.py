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
    proxy = 'no'
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
    sleep_between_iterations - дополнительный таймаут на каждые subscribe_in_session подписок
    limit_subscribes - максимальное число подписчиков у профиля (если больше, то пропустит этот профиль)
    coefficient_subscribers - подписки делённые на подписчиков (если подписок много, а подписчиков мало - пропуск)

    operating_mode - режим работы (меняет источник сбора аудитории)
    """
    operating_mode = 3

    timeout = 2
    scatter_timeout = 1
    subscribe_in_session = 40
    sleep_between_iterations = 30
    """FILTER"""
    limit_subscribes = 5000
    coefficient_subscribers = 6
    min_subscribe = 60
    min_subscribers = 60
    stop_word_dict = stop_word_dict


class SelectUser:
    delete_file = 'yes'


class Like:
    min_sleep = 10
    max_sleep = 30


class ErrorLimit:
    error_limit_unsubscribe = 5
