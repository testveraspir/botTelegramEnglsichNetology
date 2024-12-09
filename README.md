# Курсовая работа «ТГ-чат-бот «Обучалка английскому языку»» по курсу «Базы данных»

### Проект состоит из следующих файлов:
* config.env - содержит основные значения конфигурации
* parameter.py - загружает переменные из config.env
* main.py - содержит функции для взаимодействия с телеграм-ботом
* models.py - содержит код для создания базы данных
* data_db.py - содержит функции для работы с базой данных
* requirements.txt - содержит библиотеки
* documentation.md - документация по использованию программы
* images - содержит картинки для документации

### База данных состоит из трёх таблиц
![База данных](/images/schema.png)
### 1. user - таблица с пользователями:
* идентификатор пользователя в "Телеграме" (user_id)
* дата первоначального запуска бота пользователем (create_date)

### 2. dictionary - словарь:
* номер (dictionary_id)
* слово на русском (russian_word)
* слово на английском (english_word)
* идентификатор пользователя в "Телеграме", который первый добавил слово; слово из исходной таблице - 0 (user_added)

### 3. user_dictionary - таблица с словами конкретного пользователя
* номер (user_dictionary_id)
* номер слова из dictionary (dictionary_id)
* идентификатор пользователя (user_id)

## Примечание:
- Когда пользователь добавляет новое слово, если это слово с таким же переводом есть в таблице dictionary, то из таблицы берётся его id и добавляется в таблицу user_dictionary. Если в таблице dictionary нет этого слова, то сначала оно добавляется в эту таблицу.
- При удалении слова оно удаляется только из таблицы user_dictionary. В таблице dictionary остаётся (удалить может только разработчик).