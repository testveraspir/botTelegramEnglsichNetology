import random

import sqlalchemy
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from models import Base, Dictionary, UserDictionary, User


def create_session(user, password, host, port, db_name):
    try:
        dsn = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
        engine = sqlalchemy.create_engine(dsn)
        # Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session
    except Exception as ex_sess:
        print(f"Ошибка при подключении сессии. {ex_sess}")


def fill_dictionary(db_session):
    """Функция, которая заполняет словарь исходными словами."""
    translate = {"я": "i",
                 "он": "he",
                 "она": "she",
                 "для": "for",
                 "на": "on",
                 "они": "they",
                 "это": "this",
                 "из": "from",
                 "слово": "word",
                 "но": "but"
                 }
    try:
        for key, value in translate.items():
            dictionary = Dictionary(russian_word=key,
                                    english_word=value,
                                    user_added=0)
            db_session.add(dictionary)
        db_session.commit()
    except Exception as ex_fill:
        print(f"Ошибка при заполнении таблицы Dictionary исходными данными."
              f" {ex_fill}")


def add_user(db_sess, user_id):
    """Функция, которая добавляет пользователя в таблицу User."""
    try:
        user = User(user_id=user_id)
        db_sess.add(user)
        db_sess.commit()
    except Exception as ex_add_user:
        print(f"Ошибка при добавлении пользователя в базу данных."
              f" {ex_add_user}")


def get_all_id_from_initial_dictionary(db_sess):
    """Функция, которая получает все id из исходного словаря."""
    lst = []
    result = db_sess.query(Dictionary.dictionary_id).all()
    for item in result:
        lst.append(item[0])
    return lst


def fill_table_user_dictionary_initial_data(db_sess, user_id):
    """Функция, которая заполняет таблицу UserDictionary исходными данными."""
    try:
        lst_dictionary_id = get_all_id_from_initial_dictionary(db_sess)
        for dict_id in lst_dictionary_id:
            user_dictionary = UserDictionary(dictionary_id=dict_id,
                                             user_id=user_id)
            db_sess.add(user_dictionary)
            db_sess.commit()
    except Exception as ex_add_dict:
        print(f"Ошибка при добавлении исходных данных"
              f" в таблицу UserDictionary. {ex_add_dict}")


def get_id_words_for_user(db_sess, user_id):
    """Функция, которая получает список id слов
     для определённого пользователя."""
    lst_words_id = []
    result = db_sess.query(UserDictionary.dictionary_id). \
        filter(UserDictionary.user_id == user_id).all()
    for word_id in result:
        lst_words_id.append(word_id[0])
    return lst_words_id


def get_list_from_three_words(lst):
    lst_word = []
    for item in lst:
        lst_word.append(item[0])
    random.shuffle(lst_word)
    lst_word.extend(["Не хватает слов", "Не хватает слов", "Не хватает слов"])
    return lst_word[:3]


def get_words_to_check_by_user(db_sess, user_id):
    """Функция, которая получает слова для проверки."""
    lst_id = get_id_words_for_user(db_sess, user_id)
    check_word_id = random.choice(lst_id)
    result = db_sess.query(Dictionary.english_word, Dictionary.russian_word). \
        join(UserDictionary,
             UserDictionary.dictionary_id == Dictionary.dictionary_id). \
        filter(UserDictionary.user_id == user_id)
    check_word = result.filter(UserDictionary.dictionary_id == check_word_id).first()
    extra_result = result.filter(UserDictionary.dictionary_id != check_word_id).all()
    extra_words = get_list_from_three_words(extra_result)
    return check_word, extra_words


def get_id_from_user_dictionary(db_sess, word, user_id):
    """Функция, которая получает id из таблицы user_dictionary"""
    try:
        result = db_sess.query(UserDictionary.user_dictionary_id). \
            join(Dictionary,
                 UserDictionary.dictionary_id == Dictionary.dictionary_id). \
            filter(UserDictionary.user_id == user_id). \
            filter(Dictionary.russian_word == word).first()
        if not result:
            return "Такого слова или пользователя" \
                   " в таблице user_dictionary нет!"
        return result[0]
    except Exception as ex_get_word:
        print(f"Ошибка при получении id слова. {ex_get_word}")


def get_rows_by_user(db_sess, user_id):
    rows = db_sess.query(UserDictionary). \
        filter(UserDictionary.user_id == user_id).count()
    return rows


def delete_word_by_user(db_sess, word, user_id):
    """Функция, которая удаляет слово у пользователя."""
    flag = f"В базе данных слова '{word}' нет."
    rows = get_rows_by_user(db_sess, user_id)
    if rows > 1:
        try:
            word_id = get_id_from_user_dictionary(db_sess, word, user_id)
            db_sess.query(UserDictionary). \
                filter(UserDictionary.user_dictionary_id == word_id).delete()
            db_sess.commit()
            flag = f"Слово: '{word}' успешно удалено."
        except Exception as ex_del:
            print(f"Ошибка при удалении слова. {ex_del}")
            db_sess.rollback()
        return flag
    return "Вы не можете больше удалять. У Вас осталось только одно слово!!!"


def get_user(db_sess):
    """Функция, которая получает список id всех пользователей."""
    lst_users = []
    try:
        for user in db_sess.query(User.user_id).all():
            lst_users.append(user[0])
        return lst_users
    except Exception as ex_get_user:
        print(f"Ошибка при получении id пользователей. {ex_get_user}")


def get_all_rus_words_by_user(db_sess, user_id):
    """Функция, которая получает список всех русских слов у пользователя."""
    lst_rus_words = []
    try:
        result = db_sess.query(Dictionary.russian_word). \
            join(UserDictionary,
                 Dictionary.dictionary_id == UserDictionary.dictionary_id). \
            filter(UserDictionary.user_id == user_id).all()
        for word in result:
            lst_rus_words.append(word[0])
        return lst_rus_words
    except Exception as ex_rus_word:
        print(f"Ошибка при получении всех русских слов из таблицы."
              f" {ex_rus_word}")


def get_all_words_from_dictionary(db_sess):
    """Функция, которая получает список кортежей,
     состоящих из рус. и англ. слов."""
    try:
        result = db_sess.query(Dictionary.russian_word,
                               Dictionary.english_word).all()
        return result
    except Exception as ex_get_words:
        print(f"Ошибка при получении всех слов. {ex_get_words}")


def get_id_from_dictionary(db_sess, ru_word, en_word):
    """Функция, которая получает id из словаря
     одновременно по русскому и английскому словам."""
    try:
        dict_id = db_sess.query(Dictionary.dictionary_id).filter(
            and_(Dictionary.russian_word == ru_word,
                 Dictionary.english_word == en_word)).first()
        return dict_id[0]
    except Exception as e_get_id:
        print(f"Ошибка при получении id из таблицы dictionary. {e_get_id}")


def add_word_in_dictionary(db_sess, ru_word, en_word, user_id):
    """Функция, которая добавляет новое слово в словарь."""
    try:
        dictionary = Dictionary(russian_word=ru_word,
                                english_word=en_word,
                                user_added=user_id)
        db_sess.add(dictionary)
        db_sess.commit()
    except Exception as ex:
        print(f"Ошибка при добавлении слова в словарь. {ex}")


def add_word(db_sess, ru_word, en_word, user_id):
    """Функция, которая добавляет слова пользователю
     и в общий словарь (если этих слов не было)"""
    try:
        ru_words = get_all_rus_words_by_user(db_sess, user_id)
        if ru_word in ru_words:
            return f"В вашем словаре есть слово '{ru_word}'"
        if (ru_word, en_word) not in get_all_words_from_dictionary(db_sess):
            add_word_in_dictionary(db_sess, ru_word, en_word, user_id)
        dict_id = get_id_from_dictionary(db_sess, ru_word, en_word)
        user_dict = UserDictionary(dictionary_id=dict_id, user_id=user_id)
        db_sess.add(user_dict)
        db_sess.commit()
        count_word = get_rows_by_user(db_sess, user_id)
        return f"Слово '{ru_word}' успешно добавлено в базу данных!" \
               f" Количество слов в вашей базе данных {count_word}."
    except Exception as ex_add_word:
        print(f"Ошибка при добавлении слова в базу данных. {ex_add_word}")


def check_input_word(word):
    if not isinstance(word, str) or len(word) > 50 \
            or word == "" or word == " ":
        return False
    for el in word:
        if el.isdigit() or el in "!@'#$%^&*()./?":
            return False
    return True
