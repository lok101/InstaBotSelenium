import data


class StartSettings:
    """
    web_driver_wait - сколько ждать появления элемента
    """
    web_driver_wait = 30
    number_filter_iteration = 6
    sleep_page_not_found = 5
    err_proxy_timeout = 40


class Unsubscribe:
    """
    Описывает настройки, связанные с отпиской.
    min_sleep - минимальная задержка при отписке (секунды).
    max_sleep - максимальная задержка при отписке (секунды).
    sleep_between_iterations - задержка между итерациями (секунды).
    """
    min_sleep, max_sleep = 5, 11    # окно таймаутов (секунды) между подписками
    sleep_between_iterations = 3    # таймаут (минуты) между заходами


class Subscribe:

    """ Настройки для режима подписки. """
    min_timeout, max_timeout = 3, 10    # окно таймаутов (секунды) между подписками
    subscribe_in_session = 40           # количество подписок в одном заходе
    sleep_between_iterations = 15       # таймаут (минуты) между заходами
    subscribe_limit_stop = 240          # количество подписчиков у аккаунта, при котором остановится задача


class Filtered:

    """ Лимиты на посты, подписчиков, подписок у аккаунта. Аккаунты, не попавшие в лимиты, заносятся в игнор лист. """
    posts_min, posts_max = 6, 2000
    follow_min, follow_max = 50, 7000
    subs_min, subs_max = 15, 7000

    coefficient_subscribers = 6  # подписки делённые на подписчиков (если подписок много, а подписчиков мало - пропуск)
    break_limit = 100   # минимальный порог подписчиков, при превышении которого не проверяется coefficient_subscribers

    stop_word_in_nick_name_list = data.stop_word_in_nick_name   # стоп-слова для никнейма
    stop_word_in_user_name_list = data.stop_word_in_user_name   # стоп-слова для имени
    stop_word_in_biography_list = data.stop_word_in_biography   # стоп-слова для биографии

    timeout = 3


class SearchUser:

    scroll_number_subscribers_list = 3  # количество прокруток списка с пользователями во время парсинга

