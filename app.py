from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import pandas as pd
import services, config
import database as db
import sqlite3

app = Flask(__name__)

excel_file = config.EXCEL_FILE
upload_folder = config.UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_person', methods=['GET', 'POST'])
def add_person():
    if request.method == 'POST':
        fio = request.form['fio']
        position = request.form['position']
        file = request.files['photo']

        if fio and position and file and services.allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            proxy_filename = f'proxy_{filename}'
            proxy_filepath = os.path.join(config.PROXY_FOLDER, proxy_filename)
            services.convert_for_avatar(filepath, proxy_filepath)
            db.db_add_new_person(fio, position, filepath, proxy_filepath)
        return redirect(url_for('index'))
    else:
        return "Ошибка добавления данных"


@app.route('/3win_v1', methods=['GET', 'POST'])
def module_3win_v1():
    module_name = '3win_v1'
    if request.method == 'POST':
        for i in range(1, 4):
            fio = request.form[f'fio{i}']
            position = request.form[f'position{i}']
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i)
    # Чтение данных из Excel
    data = pd.read_excel(config.EXCEL_FILE).to_dict('list')
    return render_template('3win_v1.html', data=data, module_name=module_name)


@app.route('/2win_v1', methods=['GET', 'POST'])
def module_2win_v1():
    module_name = '2win_v1'
    if request.method == 'POST':
        for i in range(1, 3):
            fio = request.form[f'fio{i}']
            position = request.form[f'position{i}']
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i)
    # Чтение данных из Excel
    data = pd.read_excel(config.EXCEL_FILE).to_dict('list')
    return render_template('2win_v1.html', data=data, module_name=module_name)


@app.route('/1win_v1', methods=['GET', 'POST'])
def module_1win_v1():
    module_name = '1win_v1'
    if request.method == 'POST':
        for i in range(1, 2):
            fio = request.form[f'fio{i}']
            position = request.form[f'position{i}']
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i)
    # Чтение данных из Excel
    data = pd.read_excel(config.EXCEL_FILE).to_dict('list')
    return render_template('1win_v1.html', data=data, module_name=module_name)


@app.route('/3win_v2', methods=['GET', 'POST'])
def module_3win_v2():
    module_name = '3win_v2'
    if request.method == 'POST':
        for i in range(1, 4):
            fio = request.form[f'fio{i}']
            position = request.form[f'position{i}']
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i)
    # Чтение данных из Excel
    data = pd.read_excel(config.EXCEL_FILE).to_dict('list')
    return render_template('3win_v2.html', data=data, module_name=module_name)


@app.route('/3win_v3', methods=['GET', 'POST'])
def module_3win_v3():
    module_name = '3win_v3'
    if request.method == 'POST':
        for i in range(1, 4):
            fio = request.form[f'fio{i}']
            position = request.form[f'position{i}']
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i)
    # Чтение данных из Excel
    data = pd.read_excel(config.EXCEL_FILE).to_dict('list')
    return render_template('3win_v3.html', data=data, module_name=module_name)


@app.route('/get_people')
def get_people():
    conn = sqlite3.connect('avid.db')
    cursor = conn.cursor()
    cursor.execute("SELECT fio, position, photo, avatar FROM virt")
    people = cursor.fetchall()
    conn.close()
    return jsonify([{'fio': person[0], 'position': person[1], 'photo_path': person[2], 'proxy_path': person[3]} for person in people])


if __name__ == '__main__':
    db.db_connect()
    services.create_excel()
    app.run(debug=True)
