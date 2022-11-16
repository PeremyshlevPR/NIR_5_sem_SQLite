import sqlite3
import time
import os
from prettytable import PrettyTable


def my_factory(c, r):
    # Функция для извлечения имен полей
    d = {}

    for i, name in enumerate(c.description):
        d[name[0]] = r[i]
        d[i] = r[i]

    return d


def get_tables(dbname):
    """
    Функция для получения списка таблиц в составе БД dbname.

    :param dbname: имя базы данных
    :return: список имен таблиц, содержащихся в БД
    """

    con = sqlite3.connect(dbname)
    cur = con.cursor()

    get_tables_sql = """\
    SELECT name FROM sqlite_master WHERE type IN ('table','view')
    AND name NOT LIKE 'sqlite_%' UNION ALL SELECT name FROM
    sqlite_temp_master WHERE type IN ('table','view') ORDER BY 1;
    """

    cur.execute(get_tables_sql)
    con.commit()

    tables = cur.fetchall()
    tables_list = []
    for table in tables:
        tables_list.append(table[0])

    cur.close()
    con.close()

    return tables_list


def get_content(dbname, tabname):
    """
    Функция для получения имен полей в таблице и содержимого таблицы

    :param dbname: имя базы данных
    :param tabname: имя таблицы в базе данных
    :return: (поля таблицы, содержимое полей)
    """

    con = sqlite3.connect(dbname)
    con.row_factory = my_factory
    cur = con.cursor()

    cur.execute('SELECT * FROM ' + tabname)
    ar = cur.fetchone()
    fields = list(ar.keys())[::2]

    cur.close()
    con.close()

    con = sqlite3.connect(dbname)
    cur = con.cursor()

    cur.execute('SELECT * FROM ' + tabname)
    content = cur.fetchall()

    cur.close()
    con.close()

    return fields, content


def print_table(header, data):
    """
    Функция для вывода SQL таблицы в консоли

    :param header: список имен полей таблицы
    :param data: список кортежей с данными таблицы
    :return: None
    """
    columns = len(header)

    table = PrettyTable(header)

    td_data = data[:]

    while td_data:
        table.add_row(td_data[:columns])
        td_data = td_data[columns:]

    print(table)


def save_table(dbname, tabname, filename):
    """
    Функция для сохранения содержимого таблицы в текстовый файл.

    :param dbname: имя базы данных
    :param tabname: имя таблицы в базе данных
    :param filename: имя файла, в который будем сохранять содержимое
    :return: None
    """
    con = sqlite3.connect(dbname)
    cur = con.cursor()

    lst = []

    for row in cur.execute(f'SELECT * FROM {tabname}'):
        lst.append(row)

    with open(filename, 'w') as file:
        for x in lst:
            file.write(str(x) + '\n')

    cur.close()
    con.close()


def get_subset(dbname, tabname, expression):
    """
    Функция для получения подмножества строк из таблицы, удовлетворяющих логическому выражению.

    :param dbname: имя базы данных
    :param tabname: имя таблицы в БД
    :param expression: логическое выражение
    :return:out - список строк таблицы, удовлетворябщих выражению
    """

    con = sqlite3.connect(dbname)
    cur = con.cursor()

    sql = f"""
    SELECT * FROM {tabname}
    WHERE {expression}
    """

    cur.execute(sql)

    out = cur.fetchall()

    cur.close()
    con.close()

    return out

def remove_subset(dbname, tabname, expression):
    """
        Функция для удаления подмножества строк из таблицы, удовлетворяющих логическому выражению.

        :param dbname: имя базы данных
        :param tabname: имя таблицы в БД
        :param field: имя поля, к которому будем применять логическое выражение
        :param expression: логическое выражение
        :return: None
        """

    con = sqlite3.connect(dbname)
    cur = con.cursor()

    sql = f"""
    DELETE FROM {tabname}
    WHERE {expression}
    """

    cur.execute(sql)
    con.commit()

    cur.close()
    con.close()

def change_values(dbname, tabname, expression, field, value):
    """
    Функция, которая заменяет значения поля field на значения value в строках,
    удовлетворяющих логическому выражению expression

    :param dbname: имя базы данных
    :param tabname: имя таблицы в составе БД
    :param expression: строка с логическим выражением
    :param field: поле, в котором будем изменять значения
    :param value: значение, на которое будут заменены элементы поля field
    :return: None
    """

    con = sqlite3.connect(dbname)
    cur = con.cursor()

    sql = f"""
    UPDATE {tabname} SET 
    {field} = '{value}'
    WHERE {expression}
    """

    cur.execute(sql)
    con.commit()
    cur.close()
    con.close()

def add_row(dbname, tabname, row):
    """
    Функция для занесения новой строки в таблицу

    :param dbname: имя базы данных
    :param tabname: имя таблицы в БД
    :param row: кортеж значений, которые мы хотим внести
    :return: None
    """
    questions = ('?' for _ in row)
    question_str = ', '.join(questions)

    fields = get_content(dbname, tabname)[0]
    fields_str = ', '.join(fields)

    con = sqlite3.connect(dbname)
    cur = con.cursor()

    sql = f"INSERT INTO {tabname} (" + fields_str + ") VALUES (" + question_str + ")"

    cur.execute(sql, row)

    con.commit()

    cur.close()
    con.close()


main_menu_print = """
+-----------------------------------------------------------------------------------------+
| Выберите действие, которое хотите сделать (введите соответствующую команду)             |
|                                                                                         |
| show: Отображение содержимого таблицы БД на экране.                                     |
| save: Сохранение содержимого таблицы БД в текстовый файл.                               |
| subset: Задание условия по значениям поля таблицы и получение подмножества строк.       |
| add: Добавление новой строки с заданными значениями полей в таблицу БД.                 |
|                                                                                         |
| quit: Завершение работы с программой.                                                   |
+-----------------------------------------------------------------------------------------+
"""

#Ввод имени SQL файла
dbname = ''
while not os.path.isfile(dbname):
    dbname = input('Укажите имя файла SQLite: ')

    if os.path.isfile(dbname):
        break
    print('Нет такого файла!')

#Ввод имени таблицы
tables = get_tables(dbname)
table_name = ''
while table_name not in tables:
    print('Таблицы в базе данных:', ', '.join(tables))
    table_name = input('Укажите имя таблицы в составе БД: ')

    if table_name in tables:
        break
    print('Нет такой таблицы!')


run = True
while run:
    print(main_menu_print)
    mode_code = input('Команда: ')

    if mode_code == 'show':
        #Выводим таблицу на экран, используя модуль prettytable

        table_content = get_content(dbname, table_name)

        th = table_content[0]
        td = [item for t in table_content[1] for item in t]

        print_table(th, td)

    elif mode_code == 'save':
        #Сохраняем данные таблицы в txt файл
        file_name = input('Введите имя файла: ')

        save_table(dbname, table_name, file_name)

    elif mode_code == 'subset':
        #Получаем подмножество строк таблицы, удовлетворяющих логическому выражению
        table_content = get_content(dbname, table_name)

        print(f'Поля таблицы: {table_content[0]}')
        expression = input(f'Введите логическое выражение (пример: "age > 5", "score = 3.6", "number NOT IN (56, 45, 1, 10)"): ')

        print(f"""
        Получили подмножество строк.
        Что будем с ним делать? (Введите соответствующую команду)
        
        show: Отображение в виде таблицы
        remove: удаление из таблицы
        change: Замена всех значений поля на заданное значение
        """)

        subset_command = input('Введите команду: ')

        if subset_command == 'show':
            #Выводим на экран полученное подмножество строк

            subset = get_subset(dbname, table_name, expression)

            th = table_content[0]
            td = [item for t in subset for item in t]

            print_table(th, td)

        elif subset_command == 'remove':
            #Удаляем из ьаблицы подмножество строк

            remove_subset(dbname, table_name, expression)

        elif subset_command == 'change':
            #Заменяем значение в поле field в подмножестве

            fields = get_content(dbname, table_name)[0]

            while True:
                print(f'Поля таблицы: {fields}')
                field = input('С каким полем будем работать?')

                if field in fields:
                    break

                print('Нет такого поля!')

            value = input(f'На что вы хотите заменить значения поля {field}: ')

            change_values(dbname, table_name, expression, field, value)

        else:
            print('Неверная команда!')

    elif mode_code == 'add':
        #Добавляем новую запись в таблицу

        fields = get_content(dbname, table_name)[0]

        to_write = []

        if fields[-1] == 'note_date':
            fields = fields[:-1]

        print('Поля таблицы: ' + ', '.join(fields))

        for field in fields:
            value = input(f'Введите значение поля {field}: ')

            to_write.append(value)

        to_write.append(time.strftime("%d.%m.%Y ", time.gmtime()))
        to_write = tuple(to_write)

        add_row(dbname, table_name, to_write)

    elif mode_code == 'quit':
        #Выход из программы

        print('ВЫХОД ИЗ ПРОГРАММЫ...')
        run = False

    else:
        print('Вы ввели некорректную команду, вот список доступных команд:')