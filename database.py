import sqlite3 as sql

def db_connect():
    global db, cursor
    db = sql.connect('avid.db')
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS virt (id INTEGER PRIMARY KEY, fio TEXT, position TEXT, photo TEXT, avatar TEXT)')
    db.commit()

def db_add_new_person(fio, position, file_path, proxy_path):
    db = sql.connect('avid.db')
    cursor = db.cursor()
    try:
        cursor.execute('INSERT INTO virt (fio, position, photo, avatar) VALUES (?, ?, ?, ?)', (fio, position, file_path, proxy_path))
        db.commit()
        print('Данные успешно добавлены в базу данных')
    except sql.Error as e:
        print(f'Ошибка добавления данных в базу: {e}')
    finally:
        cursor.close()
        db.close()

def db_get_all_persons():
    db = sql.connect('avid.db')
    cursor = db.cursor()
    try:
        cursor.execute('SELECT * FROM virt')
        data = cursor.fetchall()
        return data 
    except sql.Error as e:
        print(f'Ошибка получения данных из базы: {e}')
    finally:
        cursor.close()
        db.close()
