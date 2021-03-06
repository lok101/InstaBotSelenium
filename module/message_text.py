class InformationMessage:
    page_loading_error = 'Ошибка загрузки страницы.'
    activiti_blocking = 'Микробан активности.'
    subscribe_unsubscribe_blocking = 'Микробан подписки/отписки.'
    subscribe_blocking = 'Микробан подписки.'
    unsubscribe_blocking = 'Микробан отписки.'
    page_not_exist = 'Страница не существует.'
    check_age = 'В профиле ограничение возраста.'
    task_finish = 'Задача завершена.'


class FilterMessage:
    no_avatar = 'Нет аватара.'
    no_posts = 'В профиле нет публикаций.'
    profile_closed = 'Профиль закрыт.'
    already_subscribe = 'Уже подписан.'
    filter_subs = 'Не прошёл по подпискам.'
    filter_follow = 'Не прошёл по подписчикам.'
    filter_posts = 'Не прошёл по постам.'
    bad_profile = 'Профиль "помойка".'
    stop_word_in_nick_name = 'Встречено стоп-слово в никнейме --'
    stop_word_in_user_name = 'Встречено стоп-слово в имени --'
    stop_word_in_biography = 'Встречено стоп-слово в биографии --'
    list_empty = 'В файле нет ссылок, задача завершена.'


class LoginErrorMessage:
    login_form_error = 'Ошибка авторизации.'
    error_account_name = 'Неверное имя аккаунта. Возможно, аккаунт был переименован.'
    error_pass = 'Неверный пароль.'
    not_login = 'Не получилось залогиниться.'
    broke_cookie = 'Авторизация через куки не удалась.'
    no_cookie_file = 'Куки файл ещё не создан. Логин через email-pass.'
    not_login_cookies = 'Не получилось залогиниться через Cookies.'
    not_login_page = 'Не загрузил домашнюю страницу.'
    verification_email_form = 'Поступил запрос на верификацию через Email.'
    verification_form = 'Поступил запрос на полную верификацию.'
    wrong_account = 'Авторизованный аккаунт не соответствует выбранному. Произвожу перелогин.'
