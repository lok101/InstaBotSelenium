from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from data import username, password
import random
import time


class InstagramBot:
    def __init__(self, username, password, link='https://www.instagram.com/', timeout=10):
        self.browser = webdriver.Chrome()
        self.link = link
        self.browser.implicitly_wait(timeout)
        self.username = username
        self.password = password

    def login(self):
        browser = self.browser
        browser.get(self.link)

        username_input = browser.find_element(By.NAME, 'username')
        username_input.clear()
        username_input.send_keys(username)

        password_input = browser.find_element(By.NAME, 'password')
        password_input.clear()
        password_input.send_keys(password)

        password_input.send_keys(Keys.ENTER)
        time.sleep(5)

    def close_browser(self):
        self.browser.quit()

    def unsubscribe_for_all_users(self, min_sleep=5, max_sleep=10):
        browser = self.browser
        browser.get(f"https://www.instagram.com/{username}/")

        following_count = browser.find_element(
            By.XPATH, '/html/body/div[1]/div/div/section/main/div/header/section/ul/li[3]/a/span').text
        print(f"Количество подписок: {following_count}")

        following_users_dict = {}

        while True:
            count = 10
            browser.get(f"https://www.instagram.com/{username}/")

            following_button = browser.find_element(By.XPATH, "//li[3]/a")
            following_button.click()

            # забираем все li из ul, в них хранится кнопка отписки и ссылки на подписки
            following_div_block = browser.find_element(By.XPATH, "/html/body/div[6]/div/div/div[3]/ul/div")
            following_users = following_div_block.find_elements(By.TAG_NAME, "li")

            for user in following_users:
                if not count:
                    time.sleep(10)
                    break

                user_url = user.find_element(By.TAG_NAME, "a").get_attribute("href")
                user_name = user_url.split("/")[-2]

                # добавляем в словарь пару имя_пользователя: ссылка на аккаунт
                following_users_dict[user_name] = user_url

                user.find_element(By.TAG_NAME, "button").click()
                browser.find_element(By.XPATH, "/html/body/div[7]/div/div/div/div[3]/button[1]").click()

                print(f"Итерация #{count} >>> Отписался от пользователя {user_name}")
                count -= 1
                time.sleep(random.randrange(min_sleep, max_sleep))


my_bot = InstagramBot(username, password)
try:
    my_bot.login()
    my_bot.unsubscribe_for_all_users()
finally:
    my_bot.close_browser()
