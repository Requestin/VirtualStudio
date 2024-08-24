from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
import services

app = Flask(__name__)

EXCEL_FILE = 'data/data.xlsx'
UPLOAD_FOLDER  = 'static/uploads'


@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        fio = request.form['fio']
        position = request.form['position']
        file = request.files['image']

        if file:
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            update_excel(fio, position, filepath)

        return redirect(url_for('index'))

    data = pd.read_excel(EXCEL_FILE)
    return render_template('index.html', data = data)


def update_excel(fio, position, filepath):
    df = pd.read_excel(EXCEL_FILE)

    df.at[0, '2 окна ФИО'] = fio
    df.at[0, '2 окна ДОЛЖНОСТЬ'] = position
    df.at[0, '2 окна ПУТЬ'] = filepath

    df.to_excel(EXCEL_FILE, index = False)

if __name__ == '__main__':
    services.create_excel()
    app.run(debug=True)