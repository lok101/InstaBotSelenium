from selenium.webdriver.common.by import By
from module.filter_module import FilterClass
from data import username, tag
from module.base_module import file_write
from settings import *
import time


class SupportClass(FilterClass):
    # собирает список тех, кто комменировал посты, для сбора ссылок на посты вызывает "select_url_posts_to_hashtag"
    def select_commentators(self, hashtag=tag,
                            number_scrolls=1,
                            scrolls_timeout=1,
                            delete_file=SelectUser.delete_file
                            ):
        """
        number_scrolls - колличество прокруток поля комметнариев у поста
        scrolls_timeout - задержка перед прокруткой (иначе может падать с ошибкой NoSuchElement)
        delete_file - если "yes", то очистит файл со ссылками перед записью
        """
        browser = self.browser
        link_list = self.select_url_posts_to_hashtag(hashtag=hashtag)
        if delete_file == 'yes':
            with open('data/User_urls_commentators.txt', 'w'):
                print('Файл со списком ссылок очищен.')
        for link in link_list:
            browser.get(link)
            comments_ul = self.search_element((By.XPATH, '//div[2]/div/div[2]/div[1]/ul'))

            for number in range(number_scrolls):
                time.sleep(2)
                browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", comments_ul)
                time.sleep(scrolls_timeout)

                plus_button = self.search_element((By.XPATH, '//div/div[2]/div[1]/ul/li/div/button'))
                plus_button.click()
                time.sleep(scrolls_timeout)

            # находит ссылку на профиль, опубликовавший запись, что бы кинуть его в игнор поиска по тегу
            block_profile = self.search_element((By.XPATH, '//header/div[2]/div[1]/div[1]/span/a'))
            name_profile = block_profile.get_attribute('href')

            user_urls = self.tag_search(ignore=name_profile)
            file_write('User_urls_commentators', user_urls)
            # with open('data/User_urls_commentators.txt', 'a') as file:
            #     for user_url in user_urls:
            #         file.write(user_url + '\n')
            with open('data/User_urls_commentators.txt', 'r') as file:
                size = len(file.readlines())
                print(f'Колличество собранных пользователей: {size}')

    # комплексный фильтр для режима подписки
    def assert_subscribe(self):
        # assert-функции, вывод которых прописан КАПСОМ - пишутся в лог файл
        assert self.should_be_activity_blocking(), 'Subscribe blocking'   # проверяет наличие "микробана" активности
        assert self.should_be_privat_profile(), 'Профиль закрыт.'
        assert self.should_be_subscribe(), 'Уже подписан.'
        assert self.should_be_posts(), 'В профиле нет публикаций.'
        assert self.should_be_profile_avatar(), 'Нет аватара.'
        self.should_be_compliance_with_limits()   # блок фильтов (колличество постов, подписчиков, подписок)

    # собирает список подписчиков "по конкуренту"
    def select_subscribes(self, search_name=tag,
                          delete_file=SelectUser.delete_file):
        """
        search_name - имя, которое будет вводится в строку поиска по профилям
        delete_file - если "yes", то очистит файл со ссылками перед записью
        """
        browser = self.browser
        browser.get(f"https://www.instagram.com/{username}/")

        search_input = self.search_element((By.XPATH, '//div/div/div[2]/input'))
        search_input.send_keys(search_name)
        time.sleep(5)

        public_urls = self.tag_search(ignore=username)
        time.sleep(5)
        if delete_file == 'yes':
            with open('data/User_urls_subscribers.txt', 'w'):
                print('Файл со списком ссылок очищен.')
        for url in public_urls:
            browser.get(url)
            subscribes_button = self.search_element((By.XPATH, '//header/section/ul/li[2]/a'))
            subscribes_button.click()

            subscribes_ul = self.search_element((By.XPATH, '/html/body/div[6]/div/div/div[2]'))
            browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", subscribes_ul)

            user_urls = self.tag_search(ignore=username)
            file_write('User_urls_subscribers', user_urls)
            # with open('data/User_urls_subscribers.txt', 'a') as file:
            #     for user_url in user_urls:
            #         file.write(user_url + '\n')
            with open('data/User_urls_subscribers.txt', 'r') as file:
                size = len(file.readlines())
                print(f'Колличество собранных пользователей: {size}')

    # возвращает список из 9 постов по хештегу
    def select_url_posts_to_hashtag(self, hashtag):
        browser = self.browser
        browser.get(f'https://www.instagram.com/explore/tags/{hashtag}/')
        posts_block = self.search_element((By.XPATH, '//main/article/div[1]/div/div'))
        posts = posts_block.find_elements_by_tag_name('a')
        posts_url_list = []

        for post in posts:
            post_url = post.get_attribute('href')
            if '/p/' in post_url:
                posts_url_list.append(post_url)
        print('Ссылки на посты собраны.')
        return posts_url_list
