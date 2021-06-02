from VKinder.config import sql_pass
import sqlalchemy
from pprint import pprint

db = f'postgresql://vkinder:{sql_pass}@localhost:5432/vkinder'
engine = sqlalchemy.create_engine(db)
connection = engine.connect()


def create_tables():
    connection.execute("""create table users(
                              id serial primary key,
                              user_id integer not null unique,
                              age integer not null,
                              sex integer not null,
                              city integer not null
                          );
                        
                          create table peoples(
                              id serial primary key,
                              user_id integer references users(user_id),
                              people_id integer not null
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


def select_peoples(user_id):
    data = []

    result = connection.execute(f"""SELECT people_id FROM peoples WHERE user_id = {user_id}""").fetchall()

    for i in result:
        data.append(i[0])

    return data


def select_members_peoples(user_id):
    result = connection.execute(f"""SELECT people_id FROM peoples 
                                      WHERE user_id = {user_id} AND member = 1""").fetchall()
    return result


def insert_people(user_id, people_id, member=0):
    connection.execute(f"""INSERT INTO peoples (user_id, people_id, member)
                               VALUES ({user_id}, {people_id}, {member})""")


def update_user(user_id, age, city):
    connection.execute(f"""UPDATE users
                            SET age={age},city={city} 
                            WHERE user_id={user_id};""")


# if __name__ == '__main__':
#     update_user(196844940, 28, 14)
#     print(select_members_peoples(196844940))
