from random import randrange
from getvkdata import VKData
from dblogic import VkDB
from settings import VK_GROUP_API, VK_TINDER_SAY_HI, VK_TINDER_NOT_ENOUGTH_DATA, VK_TINDER_SEARCH_ENDED

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

class VKTinder2020:

    vk_group_token = VK_GROUP_API

    def __init__(self):
        self.vk = vk_api.VkApi(token=self.vk_group_token)
        self.longpoll = VkLongPoll(self.vk)

    def write_msg(self, user_id, message):
        """Отправляет сообщение пользователю с указанным ID"""
        self.vk.method('messages.send', {'user_id': user_id, 'message': message,
                                    'random_id': randrange(10 ** 7)})

    def write_msg_attach(self, user_id, message, attach):
        """Отправляет сообщение и аттач (фото в нашем случае) пользователю с указанным ID"""
        self.vk.method('messages.send', {'user_id': user_id, 'message': message,
                                    'attachment': attach,
                                    'random_id': randrange(10 ** 7)})

    def stage_two(self, token, user_id, search_user_id):
        vk_data = VKData(token)
        vk_db = VkDB()

        sex, city, year = vk_data.get_user_info(search_user_id)
        if sex != -1:
            users_list = vk_data.search_users_by_params(sex, city, year)
            if users_list == -1:
                return -1
        else:
            return -1

        print(users_list)
        users_list = list(set(users_list) - set(vk_db.get_users_list(search_user_id)))

        user_counter = 0
        for user in users_list:
            count, photos_name_list = vk_data.get_profile_photos(user, 3)

            if count != -1:
                self.write_msg(user_id, f'Ссылка на профиль пользователя https://vk.com/id{user}')
                for photo in photos_name_list:
                    self.write_msg_attach(user_id, f'Фотография пользователя id {user}', photo[1])
                user_counter += 1
                vk_db.insert_users_list(search_user_id, user)
            else:
                print('Not enought photos')
            if user_counter == 3:
                break

        if user_counter < 3:
            return -1

    def send_standart_messages(self, user_id, type):
        """Повторяющиеся сообщения выносятся сюда для быстрого использования"""
        if type == 1:
            self.write_msg(user_id, VK_TINDER_NOT_ENOUGTH_DATA)
        if type == 2:
            self.write_msg(user_id, VK_TINDER_SEARCH_ENDED)

    def start(self):
        """Запускает бота"""

        #Очищаем ранее сохраненные данные в базе
        vk_db = VkDB()
        vk_db.clear()

        request_stage = dict()
        token = dict()
        user_list = list()

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:

                if event.to_me:
                    request = event.text
                    if not event.user_id in request_stage:
                        self.write_msg(event.user_id, VK_TINDER_SAY_HI)
                        request_stage[event.user_id] = 0
                        continue

                    if request_stage[event.user_id] == 0:
                        vk_test_key = VKData(request)
                        if vk_test_key.test_token() == -1:
                            self.write_msg(event.user_id, f"Токен указан неверный, введите его еще раз")
                        else:
                            self.write_msg(event.user_id, f"Токен принят, введите Фамилию и ИМЯ кому подобрать пару")
                            request_stage[event.user_id] = 1
                            token[event.user_id] = request
                        continue

                    if request_stage[event.user_id] == 1:
                        vk_data = VKData(token[event.user_id])
                        user_id = vk_data.find_user_by_name(request)
                        if user_id == -1:
                            self.write_msg(event.user_id, f"Не удалось распознать пользователя, введите его id")
                            request_stage[event.user_id] = 2
                        else:
                            self.write_msg(event.user_id, f"Пользователь опознан - id {user_id}")
                            res = self.stage_two(token[event.user_id], event.user_id, user_id)
                            if res == -1:
                                self.send_standart_messages(event.user_id, 1)

                            else:
                                self.send_standart_messages(event.user_id, 2)
                        continue

                    if request_stage[event.user_id] == 2:
                        print(token[event.user_id])
                        vk_data = VKData(token[event.user_id])
                        user_id = vk_data.test_token(request)
                        if user_id != -1:
                            self.write_msg(event.user_id, f"Пользователь опознан - id {user_id}")
                            res = self.stage_two(token[event.user_id], event.user_id, user_id)
                            if res == -1:
                                self.send_standart_messages(event.user_id, 1)
                                request_stage[event.user_id] = 1
                            else:
                                self.send_standart_messages(event.user_id, 2)
                                request_stage[event.user_id] = 1
                        else:
                            self.write_msg(event.user_id, f"Пользователя не удалось опознать либо профиль закрыт,"
                                                          f"попробуйте другое ФИО")
                            request_stage[event.user_id] = 1
                        continue


