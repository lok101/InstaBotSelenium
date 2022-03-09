import data


class StartSettings:

    web_driver_wait = 30
    sleep_page_not_found = 5
    err_proxy_timeout = 40


class Unsubscribe:

    """ Настройки для режима отписки. """

    min_sleep, max_sleep = 4, 10    # окно таймаутов (секунды) между подписками
    sleep_between_iterations = 3    # таймаут (минуты) между заходами (10 отписок)


class Subscribe:

    """ Настройки для режима подписки. """
    min_timeout, max_timeout = 3, 10    # окно таймаутов (секунды) между подписками
    subscribe_in_session = 40           # количество подписок в одном заходе
    sleep_between_iterations = 15       # таймаут (минуты) между заходами
    subscribe_limit_stop = 240          # количество подписчиков у аккаунта, при котором остановится задача


class Filter:

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
    iteration_for_one_account = 300


class Parce:

    scroll_number_subscribers_list = 3      # количество прокруток списка с пользователями во время парсинга
    cycles_for_one_account = 20             # количество циклов сбора через один аккаунт


# class AccountSettings:
#     parce_read_file_path = 'url_lists/subscribers_urls.txt'
#     parce_write_file_path = 'non_filtered/subscribers_urls.txt'
#     headless = True
#     proxy = True
#     accounts_key_mask = None
#     accounts_key_number = None
#     chrome_options = None
#     load_strategy = True
#     mode = None
#     exception = None
#     exception_text = None
