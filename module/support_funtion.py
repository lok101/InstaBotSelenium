from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from module.base_module import username
import data
from module.filter_module import FilterClass
from data import tag
from settings import *
import time
import re


class SupportClass(FilterClass):
    # собирает список тех, кто комменировал посты, для сбора ссылок на посты вызывает "select_url_posts_to_hashtag"
    def select_commentators(self, hashtag=tag,
                            number_scrolls=1,
                            scrolls_timeout=1,
                            ):
        """
        number_scrolls - колличество прокруток поля комметнариев у поста
        scrolls_timeout - задержка перед прокруткой (иначе может падать с ошибкой NoSuchElement)
        delete_file - если "yes", то очистит файл со ссылками перед записью
        """
        browser = self.browser
        link_list = self.select_url_posts_to_hashtag(hashtag=hashtag)
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
            self.file_write('non_filtered/user_urls_commentators', user_urls)
            with open('data/User_urls_commentators.txt', 'r') as file:
                size = len(file.readlines())
                print(f'Колличество собранных пользователей: {size}')

    # # комплексный фильтр для режима подписки
    # def assert_subscribe(self, max_coefficient=Subscribe.coefficient_subscribers,
    #                      posts_max=Subscribe.posts_max, posts_min=Subscribe.posts_min,
    #                      subscribers_max=Subscribe.subscribers_max,
    #                      subscribers_min=Subscribe.subscribers_min,
    #                      subscriptions_max=Subscribe.subscriptions_max,
    #                      subscriptions_min=Subscribe.subscriptions_min):
    #     # assert-функции, вывод которых прописан КАПСОМ - пишутся в лог файл
    #     assert self.should_be_activity_blocking(), 'Subscribe blocking'  # проверяет наличие "микробана" активности
    #     assert self.should_be_privat_profile(), 'Профиль закрыт.'
    #     assert self.should_be_subscribe(), 'Уже подписан.'
    #     assert self.should_be_posts(), 'В профиле нет публикаций.'
    #     assert self.should_be_profile_avatar(), 'Нет аватара.'
    #     # блок фильтов (колличество постов, подписчиков, подписок)
    #     self.should_be_compliance_with_limits(max_coefficient, posts_max, posts_min, subscribers_max,
    #                                           subscribers_min, subscriptions_max, subscriptions_min)

    # собирает список подписчиков "по конкуренту"
    def select_subscribes(self, search_name_list=data.tag_list, search_depth=SearchUser.search_depth,
                          max_coefficient=SearchUser.coefficient_subscribers,
                          posts_max=SearchUser.posts_max, posts_min=SearchUser.posts_min,
                          subscribers_max=SearchUser.subscribers_max,
                          subscribers_min=SearchUser.subscribers_min,
                          subscriptions_max=SearchUser.subscriptions_max,
                          subscriptions_min=SearchUser.subscriptions_min,
                          scroll_number_subscribers_list=SearchUser.scroll_number_subscribers_list
                          ):
        """
        search_name - имя, которое будет вводится в строку поиска по профилям
        delete_file - если "yes", то очистит файл со ссылками перед записью
        """
        ignore_public_url = set()
        browser = self.browser
        count_repeat_public = 0

        for search_name in search_name_list:
            print(f'--- Сбор ссылок по запросу: {search_name} ---')
            browser.get(f"https://www.instagram.com/{username}/")
            used_by_url = []

            search_input = self.search_element((By.XPATH, '//div/div/div[2]/input'))
            search_input.send_keys(search_name)

            public_urls = self.tag_search(ignore=username, parameter=1.5)
            for i in range(search_depth):
                used_by_url.append(public_urls[i - 1])

            for url in used_by_url:
                try:
                    browser.get(url)
                    user_name = url.split("/")[-2]
                    print(f'Перешёл в профиль: {user_name}', end=' ======> ')
                    if url in ignore_public_url:
                        count_repeat_public += 1
                        print(f'Дублирование профиля номер : {count_repeat_public}')
                        continue
                    ignore_public_url.add(url)
                    self.should_be_compliance_with_limits(max_coefficient, posts_max, posts_min, subscribers_max,
                                                          subscribers_min, subscriptions_max, subscriptions_min)
                    subscribes_button = self.search_element((By.XPATH, '//header/section/ul/li[2]/a'))
                    subscribes_button.click()

                    subscribes_ul = self.search_element((By.XPATH, '/html/body/div[6]/div/div/div[2]'),
                                                        type_wait=ec.presence_of_element_located)
                    for i in range(scroll_number_subscribers_list):
                        browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", subscribes_ul)
                        # выходит из цикла, когда исчезнет значок загрузки
                        while True:
                            try:
                                self.search_element((By.CSS_SELECTOR, 'li div svg.By4nA'), timeout=1,
                                                    type_wait=ec.presence_of_element_located)
                            except TimeoutException:
                                time.sleep(0.5)
                                break

                    user_urls = self.tag_search(ignore=username)
                    self.file_write('non_filtered/user_urls_subscribers', user_urls)
                    with open('data/non_filtered/user_urls_subscribers.txt', 'r') as file:
                        size = len(file.readlines())
                        print(f'Успешно. Колличество собранных пользователей: {size}')
                except AssertionError as assertion:
                    assertion = str(assertion.args)
                    text = re.sub("[)(',]", '', assertion)
                    print(text)
                    continue
                except TimeoutException:
                    print('  TimeoutException ---')
                    continue

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
