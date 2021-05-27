from VKinder.config import sql_pass
from pprint import pprint
import sqlalchemy

db = f'postgresql://vkinder:{sql_pass}@localhost:5432/vkinder'
engine = sqlalchemy.create_engine(db)
connection = engine.connect()


def create_tables():
    connection.execute("""create table peoples(
                              id serial primary key,
                              vk_id integer not null unique
                          );
                        
                          create table users(
                              id serial primary key,
                              user_id integer not null unique,
                              age integer not null,
                              sex integer not null,
                              city integer not null
                          );
                        
                        """
                       )


def select_users():
    data = []

    result = connection.execute("""SELECT user_id, age, sex, city FROM users""").fetchall()

    for i in result:
        data.append({'user_id': i[0], 'возраст': i[1], 'sex': i[2], 'город': i[3]})

    return data


def select_users_id():
    data = []

    result = connection.execute("""SELECT user_id FROM users""").fetchall()

    for i in result:
        data.append(i[0])

    return data


def insert_user(user_id, age, sex, city):
    connection.execute(f"""INSERT INTO users (user_id, age, sex, city)
                               VALUES ({user_id}, {age}, {sex}, {city});""")


if __name__ == '__main__':
    pprint(select_users())
    pprint(select_users_id())
