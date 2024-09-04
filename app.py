from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from gradio_client import Client, handle_file
from PIL import Image
import io, base64, tempfile, time, shutil, os, sqlite3, pandas as pd
import services, config, database as db

app = Flask(__name__)
client = Client("not-lain/background-removal")

EXCEL_FILE = config.EXCEL_FILE
UPLOAD_FOLDER = config.UPLOAD_FOLDER
PROXY_FOLDER = config.PROXY_FOLDER
BACKREMOVE_DELETED_PATH = config.BACKREMOVE_DELETED_PATH

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/backremove')
def backremove():
    return render_template('backremove.html')


@app.route('/add_person', methods=['GET', 'POST'])
def add_person():
    if request.method == 'POST':
        fio = request.form['fio']
        position = request.form['position']
        file = request.files['photo']

        if fio and position and file and services.allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            proxy_filename = f'proxy_{filename}'
            proxy_filepath = os.path.join(PROXY_FOLDER, proxy_filename)
            services.convert_for_avatar(filepath, proxy_filepath)
            db.db_add_new_person(fio, position, filepath, proxy_filepath)
        return redirect(url_for('index'))
    else:
        return "Ошибка добавления данных"


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
    data = pd.read_excel(EXCEL_FILE).to_dict('list')
    return render_template('1win_v1.html', data=data, module_name=module_name)


@app.route('/1win_v2', methods=['GET', 'POST'])
def module_1win_v2():
    module_name = '1win_v2'
    if request.method == 'POST':
        for i in range(1, 2):
            fio = request.form[f'fio{i}']
            position = request.form[f'position{i}']
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i)
    # Чтение данных из Excel
    data = pd.read_excel(EXCEL_FILE).to_dict('list')
    return render_template('1win_v2.html', data=data, module_name=module_name)

@app.route('/1win_v3', methods=['GET', 'POST'])
def module_1win_v3():
    module_name = '1win_v3'
    if request.method == 'POST':
        for i in range(1, 2):
            fio = request.form[f'fio{i}']
            position = request.form[f'position{i}']
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i)
    # Чтение данных из Excel
    data = pd.read_excel(EXCEL_FILE).to_dict('list')
    return render_template('1win_v3.html', data=data, module_name=module_name)


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
    data = pd.read_excel(EXCEL_FILE).to_dict('list')
    return render_template('2win_v1.html', data=data, module_name=module_name)


@app.route('/2win_v2', methods=['GET', 'POST'])
def module_2win_v2():
    module_name = '2win_v2'
    if request.method == 'POST':
        for i in range(1, 3):
            fio = request.form[f'fio{i}']
            position = request.form[f'position{i}']
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i)
    # Чтение данных из Excel
    data = pd.read_excel(EXCEL_FILE).to_dict('list')
    return render_template('2win_v2.html', data=data, module_name=module_name)


@app.route('/2win_v3', methods=['GET', 'POST'])
def module_2win_v3():
    module_name = '2win_v3'
    if request.method == 'POST':
        for i in range(1, 3):
            fio = request.form[f'fio{i}']
            position = request.form[f'position{i}']
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i)
    # Чтение данных из Excel
    data = pd.read_excel(EXCEL_FILE).to_dict('list')
    return render_template('2win_v3.html', data=data, module_name=module_name)


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
    data = pd.read_excel(EXCEL_FILE).to_dict('list')
    return render_template('3win_v1.html', data=data, module_name=module_name)


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
    data = pd.read_excel(EXCEL_FILE).to_dict('list')
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
    data = pd.read_excel(EXCEL_FILE).to_dict('list')
    return render_template('3win_v3.html', data=data, module_name=module_name)


@app.route('/get_people')
def get_people():
    conn = sqlite3.connect('avid.db')
    cursor = conn.cursor()
    cursor.execute("SELECT fio, position, photo, avatar FROM virt")
    people = cursor.fetchall()
    conn.close()
    return jsonify([{'fio': person[0], 'position': person[1], 'photo_path': person[2], 'proxy_path': person[3]} for person in people])


@app.route('/save_image', methods=['POST'])
def save_image():
    # Проверяем, есть ли данные изображения в запросе
    if 'image' not in request.json:
        # Если нет, возвращаем ошибку
        return jsonify({'success': False, 'error': 'No image data'}), 400
    # Декодируем данные изображения из base64
    image_data = base64.b64decode(request.json['image'].split(',')[1])
    # Получаем имя из данных запроса
    name = request.json['name']
    # Получаем должность из данных запроса
    position = request.json['position']
    # Создаем объект изображения из полученных данных
    img = Image.open(io.BytesIO(image_data))
    
    try:
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            # Сохраняем изображение во временный файл
            img.save(temp_file, format='PNG')
            # Получаем путь к временному файлу
            temp_file_path = temp_file.name
        # Отправляем изображение на обработку с повторными попытками
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Пытаемся обработать изображение
                result = client.predict(
                    image=handle_file(temp_file_path),
                    api_name="/image"
                )
                break  # Если успешно, выходим из цикла
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)  # Ждем 2 секунды перед повторной попыткой
                else:
                    raise  # Если все попытки не удались, вызываем исключение
        # Получаем путь к обработанному изображению
        output_image_path = result[0]
        # Формируем путь для сохранения финального изображения
        save_path = UPLOAD_FOLDER
        # Создаем директорию, если она не существует
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        # Формируем имя файла из введенных данных
        base_filename = f"{name} = {position}.png"
        final_file_path = os.path.join(save_path, base_filename)
        # Проверяем, существует ли файл с таким именем
        counter = 1
        while os.path.exists(final_file_path):
            # Если файл существует, добавляем счетчик к имени
            filename_parts = os.path.splitext(base_filename)
            final_file_path = os.path.join(save_path, f"{filename_parts[0]}_{counter}{filename_parts[1]}")
            counter += 1
        
        # Копируем обработанное изображение в финальную папку
        with Image.open(output_image_path) as img:
            img.save(final_file_path, "PNG")

        # Удаляем временные файлы
        os.remove(temp_file_path)
        os.remove(output_image_path)
        # os.remove(proxy_filepath)
        
        # Возвращаем успешный ответ с путем к сохраненному файлу
        return jsonify({'success': True, 'file_path': final_file_path})
    except Exception as e:
        # В случае ошибки возвращаем информацию об ошибке
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        # Убеждаемся, что временный файл удален в любом случае
        if 'temp_file_path' in locals():
            try:
                os.remove(temp_file_path)
            except:
                pass


# Определяем маршрут для удаления изображения, принимающий POST запросы
@app.route('/delete_image', methods=['POST'])
def delete_image():
    data = request.json
    file_path = data.get('file_path')
    comment = data.get('comment', '')

    try:
        if os.path.exists(file_path):
            # Создаем директорию DELETED, если она не существует

            deleted_path = BACKREMOVE_DELETED_PATH
            if not os.path.exists(deleted_path):
                os.makedirs(deleted_path)
            # Формируем путь для перемещения файла
            base_filename = os.path.basename(file_path)
            deleted_file_path = os.path.join(deleted_path, base_filename)
            
            # Проверяем, существует ли файл с таким именем в папке DELETED
            counter = 1
            while os.path.exists(deleted_file_path):
                filename_parts = os.path.splitext(base_filename)
                deleted_file_path = os.path.join(deleted_path, f"{filename_parts[0]}_{counter}{filename_parts[1]}")
                counter += 1
            
            # Перемещаем файл в папку DELETED
            shutil.move(file_path, deleted_file_path)
            message = f"Фото перемещено в DELETED: {deleted_file_path}"
            if comment:
                message += f" Комментарий: {comment}"
            print(message)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Файл не найден'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Определяем маршрут для получения изображения
@app.route('/get_image/<path:filename>', methods=['GET'])
def get_image(filename):
    try:
        return send_file(filename, mimetype='image/png')
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500\
        


@app.route('/continue_processing', methods=['POST'])
def continue_processing():
    data = request.json
    file_path = data.get('file_path')
    name = data.get('name')
    position = data.get('position')

    try:
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'Файл не найден'}), 404

        avatars_path = PROXY_FOLDER
        if not os.path.exists(avatars_path):
            os.makedirs(avatars_path)

        avatar_filename = os.path.basename(file_path)
        avatar_path = os.path.join(avatars_path, avatar_filename)
        services.convert_for_avatar(file_path, avatar_path)
        db.db_add_new_person(name, position, file_path=file_path, proxy_path=avatar_path)

        return jsonify({'success': True, 'avatar_path': avatar_path})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    db.db_connect()
    services.create_excel()
    app.run(debug=True, host='0.0.0.0', port=5000)
