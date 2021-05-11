import requests

class VKData:
    url = 'https://api.vk.com/method/'
    VERSION = '5.130'

    def __init__(self, token, version='5.130'):
        self.token = token
        self.version = self.VERSION
        self.params = {
            'access_token': self.token,
            'v': self.version
        }

    def test_token(self, id = 1):
        test_url = self.url + 'users.get'

        dparams = {
            'user_ids': id,
       }

        response = requests.get(test_url, params={**self.params, **dparams})
        response.raise_for_status()
        data = response.json()

        if 'error' in data:
            return -1
        else:
            return id

    def get_profile_photos(self, id_vk, count):
        '''Ограничение по количеству скачиваемых фотографий - 50
        Возвращает список URL с фотографиями
        Отдает -1, None если не удалось отправить запрос или профиль забанен, закрыт и т.д.
        '''

        if not type(id_vk) is int:
            return -1, None

        dphotos = list()
        photos_url = self.url + 'photos.get'

        photos_params = {
            'owner_id': id_vk,
            'album_id': 'profile',
            'photo_sizes': 1,
            'extended': 1,
        }

        response = requests.get(photos_url, params={**self.params, **photos_params})
        response.raise_for_status()
        data = response.json()

        if 'error' in data:
            return -1, None

        if len(data['response']['items']) < 3:
            return -1, None

        for photos in data['response']['items']:
            photo_rate, photo_name = self.__get_rating_and_photo(photos)
            dphotos.append((photo_rate, photo_name))

        return data['response']['count'], sorted(dphotos, reverse=True)[0:3]

    def __get_rating_and_photo(self, photo):
        '''Считаем рейтинг: лайк - 1 балл, комментарий - 2 балла'''
        photo_name = 'photo' + str(photo['owner_id']) + '_' + str(photo['id'])
        photo_rating = photo['likes']['count'] + 2 * photo['comments']['count']
        return photo_rating, photo_name

    def find_user_by_name(self, name):
        '''Если возникла ошибка, если 0 или несколько пользователей, то выдаем -1, что означает
        не удалось идентифицировать. Иначе возвращает id пользователя'''

        data_url = self.url + 'users.search'

        dparams = {
            'q': name,
        }
        response = requests.get(data_url, params={**self.params, **dparams})
        response.raise_for_status()
        data = response.json()

        if 'error' in data or data['response']['count'] == 0 or data['response']['count'] > 1:
            return -1

        return data['response']['items'][0]['id']

    def __key_in_dict(self, dict, *args):
        """Используется для проверки наличия всех значений в нужном словаре
        Обычно используется для проверки налчия пола, возраста и города у нужного пользователя"""
        for arg in args:
            if not arg in dict:
                return -1
        return 0

    def get_user_info(self, id_vk):

        users_url = self.url + 'users.get'

        users_params = {
            'user_ids': id_vk,
            'fields': 'sex, bdate, city'
        }

        response = requests.get(users_url, params={**self.params, **users_params})
        response.raise_for_status()
        data = response.json()

        if 'error' in data:
            return -1, -1, -1

        if self.__key_in_dict(data['response'][0], 'sex', 'city', 'bdate') == -1:
            return -1, -1, -1

        user_sex = data['response'][0]['sex']
        user_city = data['response'][0]['city']['id']
        user_year = data['response'][0]['bdate'].split('.')[-1]

        return user_sex, user_city, user_year

    def search_users_by_params(self, user_sex, user_city, user_year):
        '''Возвращает три подходящих пользователя.
        Если их меньше или ошибка, то возвращает -1'''

        user_sex = 1 if user_sex == 2 else 2

        data_url = self.url + 'users.search'

        dparams = {
            'sex': user_sex,
            'birth_year': user_year,
            'status': '6',
            'city': user_city,
            'count': 1000,
            'has_photo': 1
        }
        response = requests.get(data_url, params={**self.params, **dparams})
        response.raise_for_status()
        data = response.json()

        if 'error' in data or data['response']['count'] < 10:
            return -1

        vkid_list = list()

        for vkitem in data['response']['items']:
            if vkitem['can_access_closed'] == True:
                vkid_list.append(int(vkitem['id']))

        if len(vkid_list) > 2:
            return vkid_list
        else:
            return -1




