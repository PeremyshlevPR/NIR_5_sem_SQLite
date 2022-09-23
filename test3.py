import sqlite3
import os

def select_cmd():
    sql = 'SELECT * FROM {}'.format(tblname)
    with con:
        data = cur.execute(sql).fetchall()
    return(data)

dbname = ''

while (os.path.isfile(dbname) != True):
    dbname = input('Укажите имя файла SQLite:')
    if (os.path.isfile(dbname) == True):
        break
    print('Нет такого файла!')

tblname = input('Укажите имя таблицы:')

con = sqlite3.connect(dbname)
cur = con.cursor()

dan = select_cmd()
nzap = len(dan)

print('Таблица:', tblname, 'из БД', dbname)
for i in range(nzap):
    print(dan[i])

cur.close()
con.close()