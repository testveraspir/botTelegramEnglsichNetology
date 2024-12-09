import random

import parameter
import data_db
from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup


token_bot = parameter.token

state_storage = StateMemoryStorage()

bot = TeleBot(token_bot, state_storage=state_storage)

known_users = []
buttons = []


def show_hint(*lines):
    return '\n'.join(lines)


def show_target(data):
    return f"{data['translate_word']}  ->  {data['target_word']}"


class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'


class MyStates(StatesGroup):
    target_word = State()
    another_words = State()


@bot.message_handler(commands=['start'])
def create_cards(message):
    chat_id = message.chat.id
    if chat_id not in known_users:
        known_users.append(chat_id)

        # заполняем словарь исходными данными, если он пустой
        if not data_db.get_all_id_from_initial_dictionary(sess):
            data_db.fill_dictionary(sess)
        # если данных по пользователю нет в таблице User,
        # то заполняем таблицу User и UserDictionary исходными данными
        if chat_id not in data_db.get_user(sess):
            data_db.add_user(db_sess=sess, user_id=chat_id)
            data_db.fill_table_user_dictionary_initial_data(db_sess=sess, user_id=chat_id)
        bot.send_message(chat_id, f"Привет, {message.from_user.first_name}!"
                                  f" Давай посвятим немного времени изучению английского языка.")
    markup = types.ReplyKeyboardMarkup(row_width=2)

    global buttons
    buttons = []
    words = data_db.get_words_to_check_by_user(db_sess=sess, user_id=chat_id)
    target_word = words[0][0]
    translate = words[0][1]
    target_word_btn = types.KeyboardButton(target_word)
    buttons.append(target_word_btn)
    others = words[1]
    other_words_btns = [types.KeyboardButton(word) for word in others]
    buttons.extend(other_words_btns)
    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])

    markup.add(*buttons)

    greeting = f"Выбери перевод слова:\n🇷🇺    {translate}"
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = others


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        word = data['translate_word']
        msg = data_db.delete_word_by_user(db_sess=sess, word=word, user_id=message.chat.id)
        bot.send_message(message.chat.id, msg)
    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    chat_id = message.chat.id
    bot.set_state(message.from_user.id, MyStates.another_words, message.chat.id)
    bot.send_message(chat_id, "Введите слово на русском и через запятую его перевод, например: кот, cat")


@bot.message_handler(state=MyStates.another_words)
def add_words(message):
    chat_id = message.chat.id
    try:
        ru, en = message.text.split(", ")
        if not data_db.check_input_word(ru) or not data_db.check_input_word(en):
            raise ValueError("Некорректный ввод!!!")
        ru = ru.lower().rstrip()
        en = en.lower().strip()
        msg = data_db.add_word(db_sess=sess, ru_word=ru, en_word=en, user_id=chat_id)
        bot.send_message(message.chat.id, msg)
        bot.send_message(message.chat.id, "Для дальнейшей работы нажмите: /start или введите новое слово.")
    except ValueError as ex_val:
        print(f"Ошибка при вводе слов. {ex_val}")
        bot.send_message(message.chat.id, "Некорректный ввод. "
                                          "Попробуйте снова ввести слово и через запятую его перевод.")


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    if message.chat.id not in known_users:
        bot.send_message(message.from_user.id, "Для начала нажмите: /start")
    else:
        text = message.text
        markup = types.ReplyKeyboardMarkup(row_width=2)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            target_word = data['target_word']
            if text == target_word:
                hint = show_target(data)
                hint_text = ["Отлично! ❤", hint]
                hint = show_hint(*hint_text)
            else:
                for btn in buttons:
                    if btn.text == text:
                        btn.text = text + ' ❌'
                        break
                hint = show_hint("Допущена ошибка!",
                                 f"Попробуй ещё раз вспомнить слово 🇷🇺   {data['translate_word']}")
        markup.add(*buttons)
        bot.send_message(message.chat.id, hint, reply_markup=markup)


bot.add_custom_filter(custom_filters.StateFilter(bot))


if __name__ == "__main__":
    sess = data_db.create_session(user=parameter.user_postgresql,
                                  password=parameter.password_postgresql,
                                  host=parameter.localhost,
                                  port=parameter.port_postgresql,
                                  db_name=parameter.name_db)

    bot.infinity_polling(skip_pending=True)

    if sess:
        sess.close()
