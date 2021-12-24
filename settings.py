class StartSettings:
    """
    Описывает основные настрйки запуска.
    headless - режим "без головы" (окно браузера не запускается)
    proxy - использовать прокси или нет (сам прокси прописан в data.txt)
    implicitly_wait_timeout - сколько ждать появления элемента во всех этапах, кроме assert-функций
    """
    name_account = 'cotov'
    headless = 'no'
    proxy = 'yes'
    implicitly_wait_timeout = 10


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

    operating_mode - режим работы (меняет источник сбора аудитории)
    """
    operating_mode = 1
    timeout = 5
    scatter_timeout = 3
    subscribe_in_session = 40
    sleep_between_iterations = 50
    limit_subscribes = 5000


class SelectUser:
    delete_file = 'yes'


class Like:
    min_sleep = 10
    max_sleep = 30


class ErrorLimit:
    error_limit_unsubscribe = 5
