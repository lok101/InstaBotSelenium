import enum


class StartSettings:

    web_driver_wait = 30
    sleep_page_not_found = 5
    err_proxy_timeout = 40
    default_parameters = '-p -login'


class Unsubscribe:

    min_sleep, max_sleep = 4, 10    # окно таймаутов (секунды) между подписками
    sleep_between_iterations = 3    # таймаут (минуты) между заходами (10 отписок)


class Subscribe:

    min_timeout, max_timeout = 15, 25    # окно таймаутов (секунды) между подписками
    subscribe_in_session = 30           # количество подписок в одном заходе
    sleep_between_iterations = 30       # таймаут (минуты) между заходами
    subscribe_limit_stop = 160          # количество подписчиков у аккаунта, при котором остановится задача


class FilterLimits:

    """ Лимиты на посты, подписчиков, подписок у аккаунта. Аккаунты, не попавшие в лимиты, заносятся в игнор лист. """
    posts_min, posts_max = 6, 2000
    follow_min, follow_max = 50, 7000
    subs_min, subs_max = 15, 7000

    coefficient_subscribers = 6  # подписки делённые на подписчиков (если подписок много, а подписчиков мало - пропуск)
    break_limit = 100   # минимальный порог подписчиков, при превышении которого не проверяется coefficient_subscribers

    timeout = 3
    iteration_for_one_account = 300


class Parce:

    scroll_number_subscribers_list = 3      # количество прокруток списка с пользователями во время парсинга
    cycles_for_one_account = 20             # количество циклов сбора через один аккаунт


class LoginFrom(enum.Enum):
    form_login = 0
    chrome_profile = 1

