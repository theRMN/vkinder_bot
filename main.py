import vk_api
from config import group_token
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange

session = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(session)


def write_msg(user_id, message):
    session.method('messages.send',
                   {'user_id': user_id,
                    'message': message,
                    'random_id': randrange(10 ** 7)})


def get_users(user_id):
    data = session.method('users.get',
                          {'user_ids': user_id,
                           'fields': 'bdate,sex,city,relation'})
    return data


def search_users(age_from, age_to, sex, city, status):
    data = session.method('users.search',
                          {'age_from': age_from,
                           'age_to': age_to,
                           'sex': sex,
                           'city': city,
                           'status': status,
                           'count': 1})
    return data


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text.lower()

            if request == '/h':
                write_msg(event.user_id, f'===== Список комманд =====\n'
                                         f'/h - помощ\n'
                                         f'/s - поиск пользователей VK\n')

            elif request == '/s':
                search_users(19, 25, 1, 144, 1)
                # get_users('8430489')
                write_msg(event.user_id, 'ок')
