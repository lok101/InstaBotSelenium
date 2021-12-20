from selenium.webdriver.common.by import By
from module.base_module import BaseClass
from data import username, tag
import time


class SupportClass(BaseClass):
    # собирает список тех, кто комменировал посты, для сбора ссылок на посты вызывает "select_url_posts_to_hashtag"
    def select_commentators(self, hashtag=tag, number_scrolls=1, scrolls_timeout=1):
        """
        number_scrolls - колличество прокруток поля комметнариев у поста
        scrolls_timeout - задержка перед прокруткой (иначе может падать с ошибкой NoSuchElement)
        """
        browser = self.browser
        link_list = self.select_url_posts_to_hashtag(hashtag=hashtag)
        for link in link_list:
            browser.get(link)
            comments_ul = browser.find_element(By.XPATH, '//div[2]/div/div[2]/div[1]/ul')

            for number in range(number_scrolls):
                browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", comments_ul)
                time.sleep(scrolls_timeout)

                plus_button = browser.find_element(By.XPATH, '//div/div[2]/div[1]/ul/li/div/button')
                plus_button.click()
                time.sleep(scrolls_timeout)

            user_urls = self.tag_search()
            with open('data/User_urls_commentators.txt', 'a') as file:
                for user_url in user_urls:
                    file.write(user_url + '\n')
                size = len(file.readlines())
                print(f'Колличество собранных пользователей: {size}')

    # собирает список подписчиков "по конкуренту"
    def select_subscribes(self, search_name=tag):
        browser = self.browser
        browser.get(f"https://www.instagram.com/{username}/")

        search_input = browser.find_element(By.XPATH, '//div/div/div[2]/input')
        search_input.send_keys(search_name)

        public_urls = self.tag_search()

        for url in public_urls:
            browser.get(url)
            subscribes_button = browser.find_element(By.XPATH, '//header/section/ul/li[2]/a')
            subscribes_button.click()

            subscribes_ul = browser.find_element(By.XPATH, '/html/body/div[6]/div/div/div[2]')
            browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", subscribes_ul)

            user_urls = self.tag_search()
            with open('data/User_urls_subscribers.txt', 'a') as file:
                for user_url in user_urls:
                    file.write(user_url + '\n')
                size = len(file.readlines())
                print(f'Колличество собранных пользователей: {size}')

    # возвращает список из девяти постов по хештегу
    def select_url_posts_to_hashtag(self, hashtag):
        browser = self.browser
        browser.get(f'https://www.instagram.com/explore/tags/{hashtag}/')
        posts_block = browser.find_element(By.XPATH, '//main/article/div[1]/div/div')
        posts = posts_block.find_elements_by_tag_name('a')
        posts_url_list = []

        for post in posts:
            post_url = post.get_attribute('href')
            if '/p/' in post_url:
                posts_url_list.append(post_url)
        print('Ссылки на посты собраны.')
        return posts_url_list
