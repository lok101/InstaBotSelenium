from selenium.webdriver.common.by import By


class Login:
    username = (By.NAME, "username")
    password = (By.NAME, "password")
    button_cookie_accept = (By.CSS_SELECTOR, 'button.aOOlW.HoLwm')
    label_about_error_under_login_button = (By.CSS_SELECTOR, '#slfErrorAlert')


class UserPage:
    instagram_logo = (By.CSS_SELECTOR, '[href=\'/\']')
    account_photo = (By.CSS_SELECTOR, 'div.eC4Dz img')
    user_name = (By.CSS_SELECTOR, 'div.QGPIr > span')
    user_biography = (By.CSS_SELECTOR, 'div.QGPIr > div')

    posts = (By.CSS_SELECTOR, 'li:nth-child(1) > div > span.g47SY')
    followers = (By.CSS_SELECTOR, 'li:nth-child(2) > a > div > span.g47SY')
    subscriptions = (By.CSS_SELECTOR, 'li:nth-child(3) > a > div > span.g47SY')
    label_this_close_account = (By.XPATH, '//article/div[1]/div/h2')

    button_to_open_subscriptions_list = (By.XPATH, "//li[3]/a")
    subscriptions_list_div_block = (By.CSS_SELECTOR, "div > div > div.isgrP > ul > div")
    button_unsubscribe = (By.CSS_SELECTOR, 'span.vBF20._1OSdk > button')
    button_confirm_unsubscribe = (By.CSS_SELECTOR, "button.-Cab_")

    all_buttons = (By.CSS_SELECTOR, 'div button')
    home_button = (By.CSS_SELECTOR, 'div.ctQZg.KtFt3 > div > div:nth-child(1)')

    button_to_open_followers_list = (By.CSS_SELECTOR, 'li:nth-child(2) > a')
    followers_list_div_block = (By.CSS_SELECTOR, 'div.RnEpo.Yx5HN > div > div > div> div.isgrP')
    followers_list_progress_bar_icon = (By.CSS_SELECTOR, 'li div svg.By4nA')


class Technical:
    info_field_of_ip_address = (By.TAG_NAME, "body")
    tag_a = (By.TAG_NAME, 'a')
    tag_li = (By.TAG_NAME, "li")
    button_subscribe_into_followers_list_div_block = (By.CSS_SELECTOR, 'div.Pkbci > button')

    header_on_stop_page = (By.CSS_SELECTOR, 'div > div.error-container > p')
    header_on_page_close = (By.CSS_SELECTOR, 'div > div > h2')   # ссылка устарела, аккаунт закрыт, ограничение возраст
    alert_window_activity_blocking = (By.CSS_SELECTOR, 'div._08v79 > h3')
    button_exit_from_account_on_verification_query_page = (By.CSS_SELECTOR, 'section > div > div > div.erQwt > a')
    cookie_accept_window = (By.CSS_SELECTOR, 'div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div > span')
