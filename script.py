import sqlite3

# файл создан исключительно для разовых использований функции обращения к базе данных
# для разовых созданий или записей в базу данных новых данных
# файл нужен на этап разработки и отладки, чтобы не тратить время на повторные запросы
# и тестовые записи в таблицу, здесь приведены почти все команды,
# которые использовались для базы данных во время разработки проекта


# вчитываться и разбираться в коде не обязательно, вся визуальная состовляющая кода этого файла
# никак не учитывается, за помощью в использовании скрипта стоит обратиться к автору кода
# @Puhon


with sqlite3.connect('VeritasDB.db') as conn:
    cursor = conn.cursor()

    # create_table = """
    #     CREATE TABLE IF NOT EXISTS students (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         name TEXT NOT NULL,
    #         vusGroup TEXT NOT NULL,
    #         lbs TEXT NOT NULL
    #     )
    # """ # это команда, с помощью которой я создал таблицу

    '''
    тут кароче дословно:
        создать таблицу если ещё нет с именем students с параметрами (
            id число, ключ, автозаполнение,
            имя текст, не пустое,
            группа текст, не пустое,
            лабы текст, не пустое
        )
    '''

    create_table = """
        CREATE TABLE IF NOT EXISTS verifyed_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT NOT NULL,
            group_num TEXT NOT NULL,
            password TEXT NOT NULL,
            lab1 FLOAT DEFAULT 0.0,
            lab2 FLOAT DEFAULT 0.0,
            lab3 FLOAT DEFAULT 0.0,
            lab4 FLOAT DEFAULT 0.0,
            rating FLOAT DEFAULT 0.0
        )
    """

    # create_table = """
    #     CREATE TABLE IF NOT EXISTS generated_keys (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         key TEXT NOT NULL
    #     )
    # """

    # create_table = """
    #     CREATE TABLE IF NOT EXISTS generated_keys (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         key TEXT NOT NULL
    #     )
    # """



    add_info = """
        INSERT INTO verifyed_users (login, password) VALUES (?, ?)
    """ # эта строка нужна для добавления инфы в таблицу
    add_info = """
        INSERT INTO generated_keys (key) VALUES (?)
    """ # эта строка нужна для добавления инфы в таблицу
    command = create_table
    # command = add_info
    cursor.execute(create_table)
    # cursor.execute(command, ("key",)) # добавляем инфу в таблицу
    # 1 1 1 1 0 0 0 - это из 7 лаб какие зач какие нзач, потом сам форматирую это

    #-----------------------------------------------------------------------
    #------------- запустите скрипт и посмотрите консоль -------------------
    #-----------------------------------------------------------------------
    # Получаем список всех таблиц в базе данных
    # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    # tables = cursor.fetchall()

    # # Для каждой таблицы извлекаем имена столбцов и данные
    # for table in tables:
    #     table_name = table[0]
    #     print(f"\nТаблица: {table_name}")
        
    #     # Получаем имена столбцов
    #     cursor.execute(f"PRAGMA table_info({table_name});")
    #     columns = cursor.fetchall()
        
    #     column_names = [col[1] for col in columns]
    #     print(f"{' | '.join(column_names)}")

    #     # Получаем все строки из таблицы
    #     cursor.execute(f"SELECT * FROM {table_name};")
    #     rows = cursor.fetchall()

    #     # Выводим строки
    #     for row in rows:
    #         print(f"{' | '.join(map(str, row))}")



    conn.commit()

