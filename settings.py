from data import stop_word_dict


class StartSettings:
    """
    web_driver_wait - сколько ждать появления элемента
    """
    web_driver_wait = 30
    filtered_user_list_timeout = 1
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
    min_sleep = 5
    max_sleep = 11
    sleep_between_iterations = 150


class Subscribe:
    """
    Описывает настройки, связанные с подпиской.
    min_timeout, max_timeout - окно таймаутов между подписками
    subscribe_in_session - количество подписок в одном заходе
    sleep_between_iterations - таймаут на каждые subscribe_in_session подписок

    FILTER
    limit_subscribes_min, limit_subscribes_max - максимальное и минимальное число подписчиков для профиля
    limit_posts_min, limit_posts_max - максимальное и минимальное число постов для профиля
    coefficient_subscribers - подписки делённые на подписчиков (если подписок много, а подписчиков мало - пропуск)
    subscribe_limit - количество подписок в задаче
    break_limit - минимальный порог подписчиков, при превышении которого не проверяется coefficient_subscribers

    """
    min_timeout = 3
    max_timeout = 10
    subscribe_in_session = 40
    sleep_between_iterations = 15
    subscribe_limit_stop = 240
    """FILTER"""
    subscribers_min, subscribers_max = 50, 7000
    subscriptions_min, subscriptions_max = 50, 7000
    posts_min, posts_max = 6, 800
    coefficient_subscribers = 6
    min_subscribers = 60
    min_subscriptions = 60
    break_limit = 100
    stop_word_dict = stop_word_dict


class SearchUser:
    """
    search_depth - количество профилей из меню поиска, попадающих в выборку, при сборе аудитории
    scroll_number_subscribers_list - число прокруток, при открытии списка подписчиков (больше прокруток - больше юзеров)

    limit_subscribes_min, limit_subscribes_max - максимальное и минимальное число подписчиков для профиля
    limit_posts_min, limit_posts_max - максимальное и минимальное число постов для профиля
    coefficient_subscribers - подписки делённые на подписчиков (если подписок много, а подписчиков мало - пропуск)
    subscribe_limit - количество подписок в задаче
    break_limit - минимальный порог подписчиков, при превышении которого не проверяется coefficient_subscribers
    """
    scroll_number_subscribers_list = 3
    """FILTER"""
    coefficient_subscribers = 1
    posts_max, posts_min = 1000000, 3
    subscribers_max, subscribers_min = 100000, 1000
    subscriptions_max, subscriptions_min = 1200, 0
    break_limit = 1000
    search_depth = 10

    timeout_between_restarts = 10
    number_restart_filtered = 10


class Like:
    min_sleep = 10
    max_sleep = 30
