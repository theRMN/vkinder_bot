from SQL.vkinderBase import select_users_id, select_users, insert_user, select_peoples, insert_people, update_user
from vk_api.longpoll import VkLongPoll, VkEventType
from config import group_token, app_token
from random import randrange
from datetime import date
import vk_api

session = vk_api.VkApi(token=group_token)
session_2 = vk_api.VkApi(token=app_token)

longpoll = VkLongPoll(session)


def get_request(lp=longpoll):
    for event in lp.listen():
        if event.type == VkEventType.MESSAGE_NEW:

            if event.to_me:
                request = event.text.lower()

                return request


def write_msg(user_id, message):
    session.method('messages.send',
                   {'user_id': user_id,
                    'message': message,
                    'random_id': randrange(10 ** 7)})


def write_img(user_id, owner_id, media_id):
    session.method('messages.send',
                   {'user_id': user_id,
                    'attachment': f'photo{owner_id}_{media_id}',
                    'random_id': randrange(10 ** 7)})


def get_users(user_id):
    data = session.method('users.get',
                          {'user_ids': user_id,
                           'fields': 'bdate,sex,country,city,relation'})

    return data


def search_users(age=0, sex=0, city=0):
    if sex == 2:
        sex = 1
    else:
        sex = 2

    request = session_2.method('users.search',
                               {'age_from': age - 1,
                                'age_to': age + 1,
                                'sex': sex,
                                'city': city,
                                'status': 6,
                                'count': 1000,
                                'fields': 'photo_max_orig'})

    data = {'items': []}

    for i in request['items']:
        if i['is_closed'] is False:
            data['items'].append(i)

    return data['items']


def get_city_from_id(country, city):
    data = session_2.method('database.getCities',
                            {'country_id': country,
                             'q': city,
                             'count': 1})

    city_id = data['items'][0]['id']
    return city_id


def get_photos(user_id):
    request = session_2.method('photos.getAll', {'owner_id': user_id,
                                                 'offset': 0,
                                                 'count': 200,
                                                 'photo_sizes': 1,
                                                 'extended': 1,
                                                 'v': 5.131})

    result = {}

    for i in request['items']:
        result[i['id']] = i['likes']['count']

    return sorted(result)[-4: -1]


def send_hello(event):
    name = get_users(event.user_id)[0]['first_name']
    write_msg(event.user_id, f'Привет, {name}!\n Для того, чтобы увидеть список комманд введи "/h"')
    return


def send_menu(event):
    write_msg(event.user_id, f'===== Список комманд =====\n'
                             f'/p - рандомная картинка\n'
                             f'/s - поиск\n'
                             f'/n - следующий человек в поиске\n'
                             f'/m - добавить в избраное\n'
                             f'/ch - изменить пользовательские днные\n')
    return


def send_picture(event):
    write_msg(event.user_id, 'Не, ну не всё сразу....')
    return


def send_search(event):
    data = {'first_name': None,
            'id': None,
            'last_name': None,
            'sex': None,
            'country': None,
            'город': None,
            'возраст': None}

    if event.user_id not in select_users_id():

        for i in get_users(event.user_id)[0].items():
            data[i[0]] = i[1]
            if i[0] == 'bdate' and len(i[1].split('.')[-1]) == 4:
                data['возраст'] = date.today().year - int(i[1].split('.')[-1])

        country_id = get_users(event.user_id)[0]['country']['id']

        for i in data.items():
            if i[1] is None:
                write_msg(event.user_id, f'Введите свой {i[0]}')

                request = get_request()

                if i[0] == 'город':
                    data['город'] = get_city_from_id(country_id, request)
                elif i[0] == 'возраст' and int(request) > 70:
                    write_msg(event.user_id, 'Слишком большое значение возраста, попробуйте снова')
                else:
                    data[i[0]] = request

        insert_user(event.user_id, data['возраст'], data['sex'], data['город'])

    else:
        for i in select_users():
            if i['user_id'] == event.user_id:
                data['sex'] = i['sex']
                data['возраст'] = i['возраст']
                data['город'] = i['город']

    for i in search_users(int(data['возраст']), data['sex'], data['город']):
        first_name = i['first_name']
        last_name = i['last_name']
        link = 'vk.com/id' + str(i['id'])

        if int(i['id']) not in select_peoples(event.user_id):
            write_msg(event.user_id, f'{first_name} {last_name} - {link}\n')

            for photo in get_photos(str(i['id'])):
                write_img(event.user_id, str(i['id']), photo)

            request_member = get_request()

            if request_member == '/m':
                insert_people(event.user_id, int(i['id']), 1)
            elif request_member == '/n':
                insert_people(event.user_id, int(i['id']))
            else:
                return

        else:
            continue


def change_user_data(event):
    country_id = get_users(event.user_id)[0]['country']['id']
    age = ''
    city = ''

    write_msg(event.user_id, 'Текущие данные:')
    for i in select_users():
        if i['user_id'] == event.user_id:
            age = i['возраст']
            city = i['город']
            write_msg(event.user_id, f'Возраст: {age}\nГород: {city}')

    write_msg(event.user_id, 'Что нужно поменять ?')

    request = get_request()

    if request == 'город':
        write_msg(event.user_id, 'Введите новый город:')

        request_city = get_request()
        new_city = get_city_from_id(country_id, request_city)

        update_user(event.user_id, int(age), int(new_city))

        write_msg(event.user_id, 'Город успешно изменён')
    elif request == 'возраст':
        write_msg(event.user_id, 'Введите новый возраст:')

        request_age = get_request()
        if int(request_age) > 70:
            write_msg(event.user_id, 'Слишком большое значение возраста, попробуйте снова')
        else:
            update_user(event.user_id, int(request_age), int(city))
            write_msg(event.user_id, 'Возраст успешно изменён')
    else:
        return
    change_user_data(event)


def execute():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:

            if event.to_me:
                request = event.text.lower()

                try:
                    if request in ['начать', 'привет']:
                        send_hello(event)
                    elif request == '/h':
                        send_menu(event)
                    elif request == '/p':
                        send_picture(event)
                    elif request == '/s':
                        send_search(event)
                    elif request == '/ch':
                        change_user_data(event)
                except IndexError:
                    write_msg(event.user_id, 'Неправильное название города, попробуйте снова')
                    continue
                except ValueError:
                    write_msg(event.user_id, 'Возраст может быть только числом, попробуйте снова')
                    continue
                except TypeError:
                    continue


if __name__ == '__main__':
    execute()
