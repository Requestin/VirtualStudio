import sqlite3 as sql

def db_connect():
    global db, cursor
    db = sql.connect('avid.db')
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS virt (id INTEGER PRIMARY KEY, fio TEXT, position TEXT, photo TEXT, avatar TEXT)')
    db.commit()

