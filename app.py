from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import io, base64, tempfile, time, shutil, os, sqlite3, pandas as pd
import services, config, database as db

# Импортируем локальный обработчик
from backremoval.background_removal.app import process_file

app = Flask(__name__)

UPLOAD_FOLDER = config.UPLOAD_FOLDER
PROXY_FOLDER = config.PROXY_FOLDER
BACKREMOVE_DELETED_PATH = config.BACKREMOVE_DELETED_PATH

# Функция для создания заглушки изображения с текстом
def create_placeholder_image(text, filename, size=(200, 200), bg_color=(0, 35, 75), text_color=(255, 255, 255)):
    img_path = os.path.join('static', 'images', filename)
    
    # Не создаем файл, если он уже существует
    if os.path.exists(img_path):
        return
    
    # Создаем изображение с заданным фоном
    img = Image.new('RGB', size, color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Пытаемся использовать шрифт, если он доступен
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        # Используем стандартный шрифт, если arial не найден
        font = ImageFont.load_default()
    
    # Вычисляем положение текста для центрирования
    text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else (50, 20)
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    # Рисуем текст
    draw.text(position, text, fill=text_color, font=font)
    
    # Создаем папку images, если она не существует
    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    
    # Сохраняем изображение
    img.save(img_path)

# Создаем заглушки при запуске приложения, если их нет
def init_placeholder_images():
    create_placeholder_image("Favicon", "favicon.png", size=(32, 32))
    create_placeholder_image("РЕН ТВ", "rentv_logo.png", size=(100, 100))
    create_placeholder_image("5 КАНАЛ", "5tv_logo.png", size=(100, 100))

# Инициализация заглушек при запуске
init_placeholder_images()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/channel/<channel>')
def channel_modules(channel):
    if channel in config.CHANNELS:
        channel_name = config.CHANNELS[channel]['name']
        return render_template('channel_modules.html', channel=channel, channel_name=channel_name)
    else:
        return redirect(url_for('index'))

@app.route('/backremove')
def backremove():
    return render_template('backremove.html')

@app.route('/delete_person')
def delete_person_page():
    return render_template('delete_person.html')

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


@app.route('/<channel>/1win_v1', methods=['GET', 'POST'])
def module_1win_v1(channel):
    if channel not in config.CHANNELS:
        return redirect(url_for('index'))
        
    module_name = '1win_v1'
    if request.method == 'POST':
        for i in range(1, 2):
            fio = request.form[f'fio{i}']
            position = request.form[f'position{i}']
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i, channel)
    # Чтение данных из Excel
    excel_file = config.CHANNELS[channel]['excel']
    data = pd.read_excel(excel_file).to_dict('list')
    channel_name = config.CHANNELS[channel]['name']
    return render_template('1win_v1.html', data=data, module_name=module_name, channel=channel, channel_name=channel_name)


@app.route('/<channel>/1win_v2', methods=['GET', 'POST'])
def module_1win_v2(channel):
    if channel not in config.CHANNELS:
        return redirect(url_for('index'))
        
    module_name = '1win_v2'
    if request.method == 'POST':
        for i in range(1, 2):
            fio = request.form[f'fio{i}']
            position = request.form[f'position{i}']
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i, channel)
    # Чтение данных из Excel
    excel_file = config.CHANNELS[channel]['excel']
    data = pd.read_excel(excel_file).to_dict('list')
    channel_name = config.CHANNELS[channel]['name']
    return render_template('1win_v2.html', data=data, module_name=module_name, channel=channel, channel_name=channel_name)

@app.route('/<channel>/1win_v3', methods=['GET', 'POST'])
def module_1win_v3(channel):
    if channel not in config.CHANNELS:
        return redirect(url_for('index'))
        
    module_name = '1win_v3'
    if request.method == 'POST':
        for i in range(1, 2):
            fio = request.form[f'fio{i}']
            position = request.form[f'position{i}']
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i, channel)
    # Чтение данных из Excel
    excel_file = config.CHANNELS[channel]['excel']
    data = pd.read_excel(excel_file).to_dict('list')
    channel_name = config.CHANNELS[channel]['name']
    return render_template('1win_v3.html', data=data, module_name=module_name, channel=channel, channel_name=channel_name)


@app.route('/<channel>/2win_v1', methods=['GET', 'POST'])
def module_2win_v1(channel):
    if channel not in config.CHANNELS:
        return redirect(url_for('index'))
        
    module_name = '2win_v1'
    if request.method == 'POST':
        for i in range(1, 3):
            fio = request.form[f'fio{i}']
            position = request.form[f'position{i}']
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i, channel)
    # Чтение данных из Excel
    excel_file = config.CHANNELS[channel]['excel']
    data = pd.read_excel(excel_file).to_dict('list')
    channel_name = config.CHANNELS[channel]['name']
    return render_template('2win_v1.html', data=data, module_name=module_name, channel=channel, channel_name=channel_name)


@app.route('/<channel>/2win_v2', methods=['GET', 'POST'])
def module_2win_v2(channel):
    if channel not in config.CHANNELS:
        return redirect(url_for('index'))
        
    module_name = '2win_v2'
    if request.method == 'POST':
        for i in range(1, 3):
            fio = request.form[f'fio{i}']
            position = request.form[f'position{i}']
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i, channel)
    # Чтение данных из Excel
    excel_file = config.CHANNELS[channel]['excel']
    data = pd.read_excel(excel_file).to_dict('list')
    channel_name = config.CHANNELS[channel]['name']
    return render_template('2win_v2.html', data=data, module_name=module_name, channel=channel, channel_name=channel_name)


@app.route('/<channel>/2win_v3', methods=['GET', 'POST'])
def module_2win_v3(channel):
    if channel not in config.CHANNELS:
        return redirect(url_for('index'))
        
    module_name = '2win_v3'
    if request.method == 'POST':
        for i in range(1, 3):
            fio = request.form[f'fio{i}']
            position = request.form[f'position{i}']
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i, channel)
    # Чтение данных из Excel
    excel_file = config.CHANNELS[channel]['excel']
    data = pd.read_excel(excel_file).to_dict('list')
    channel_name = config.CHANNELS[channel]['name']
    return render_template('2win_v3.html', data=data, module_name=module_name, channel=channel, channel_name=channel_name)


@app.route('/<channel>/3win_v1', methods=['GET', 'POST'])
def module_3win_v1(channel):
    if channel not in config.CHANNELS:
        return redirect(url_for('index'))
        
    module_name = '3win_v1'
    if request.method == 'POST':
        for i in range(1, 4):
            fio = request.form[f'fio{i}']
            position = request.form[f'position{i}']
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i, channel)
    # Чтение данных из Excel
    excel_file = config.CHANNELS[channel]['excel']
    data = pd.read_excel(excel_file).to_dict('list')
    channel_name = config.CHANNELS[channel]['name']
    return render_template('3win_v1.html', data=data, module_name=module_name, channel=channel, channel_name=channel_name)


@app.route('/<channel>/3win_v2', methods=['GET', 'POST'])
def module_3win_v2(channel):
    if channel not in config.CHANNELS:
        return redirect(url_for('index'))
        
    module_name = '3win_v2'
    if request.method == 'POST':
        for i in range(1, 4):
            fio = request.form[f'fio{i}']
            position = request.form[f'position{i}']
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i, channel)
    # Чтение данных из Excel
    excel_file = config.CHANNELS[channel]['excel']
    data = pd.read_excel(excel_file).to_dict('list')
    channel_name = config.CHANNELS[channel]['name']
    return render_template('3win_v2.html', data=data, module_name=module_name, channel=channel, channel_name=channel_name)


@app.route('/<channel>/3win_v3', methods=['GET', 'POST'])
def module_3win_v3(channel):
    if channel not in config.CHANNELS:
        return redirect(url_for('index'))
        
    module_name = '3win_v3'
    if request.method == 'POST':
        for i in range(1, 4):
            fio = request.form[f'fio{i}']
            position = request.form[f'position{i}']
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i, channel)
    # Чтение данных из Excel
    excel_file = config.CHANNELS[channel]['excel']
    data = pd.read_excel(excel_file).to_dict('list')
    channel_name = config.CHANNELS[channel]['name']
    return render_template('3win_v3.html', data=data, module_name=module_name, channel=channel, channel_name=channel_name)


@app.route('/get_people')
def get_people():
    conn = sqlite3.connect('avid.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, fio, position, photo, avatar FROM virt ORDER BY fio COLLATE NOCASE")
    people = cursor.fetchall()
    conn.close()
    return jsonify([{'id': person[0], 'fio': person[1], 'position': person[2], 'photo_path': person[3], 'proxy_path': person[4]} for person in people])


@app.route('/save_image', methods=['POST'])
def save_image():
    data = request.get_json()
    image_data = data.get('image')
    name = data.get('name', 'noname')
    position = data.get('position', 'noposition')

    try:
        # Декодируем base64 изображение и сохраняем во временный файл
        header, encoded = image_data.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(img_bytes)
            temp_file_path = temp_file.name

        # Локальная обработка изображения (удаление фона)
        output_image_path = process_file(temp_file_path)  # Возвращает путь к PNG

        # Формируем путь для сохранения финального изображения
        save_path = UPLOAD_FOLDER
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        base_filename = f"{name} = {position}.png"
        final_file_path = os.path.join(save_path, base_filename)

        # Проверяем, существует ли файл с таким именем
        counter = 1
        while os.path.exists(final_file_path):
            filename_parts = os.path.splitext(base_filename)
            final_file_path = os.path.join(save_path, f"{filename_parts[0]}_{counter}{filename_parts[1]}")
            counter += 1

        # Открываем обработанное изображение и сохраняем в нужную папку
        with Image.open(output_image_path) as img:
            img.save(final_file_path, "PNG")

        # === СОЗДАЁМ АВАТАР ===
        avatar_path = os.path.join(PROXY_FOLDER, os.path.splitext(os.path.basename(final_file_path))[0] + ".jpg")
        services.convert_for_avatar(final_file_path, avatar_path)

        # Удаляем временные файлы
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        if os.path.exists(output_image_path):
            os.remove(output_image_path)

        # Возвращаем успешный ответ с путями к файлам
        return jsonify({'success': True, 'file_path': final_file_path, 'avatar_path': avatar_path})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
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

            # === УДАЛЯЕМ СООТВЕТСТВУЮЩУЮ АВАТАРКУ ===
            avatar_path = os.path.join(PROXY_FOLDER, os.path.splitext(os.path.basename(file_path))[0] + ".jpg")
            if os.path.exists(avatar_path):
                try:
                    os.remove(avatar_path)
                    print(f"Аватарка {avatar_path} удалена.")
                except Exception as e:
                    print(f"Ошибка при удалении аватарки: {e}")

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

        # Формируем путь к уже существующему аватару
        avatar_path = os.path.join(PROXY_FOLDER, os.path.splitext(os.path.basename(file_path))[0] + ".jpg")
        db.db_add_new_person(name, position, file_path=file_path, proxy_path=avatar_path)

        return jsonify({'success': True, 'avatar_path': avatar_path})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete_person', methods=['POST'])
def delete_person():
    data = request.json
    person_id = data.get('id')
    
    if not person_id:
        return jsonify({'success': False, 'error': 'ID не указан'}), 400
    
    try:
        # Получаем информацию о человеке перед удалением
        conn = sqlite3.connect('avid.db')
        cursor = conn.cursor()
        cursor.execute("SELECT photo, avatar FROM virt WHERE id = ?", (person_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'success': False, 'error': 'Человек не найден'}), 404
            
        photo_path, avatar_path = result
        
        # Удаляем файлы, если они существуют
        if photo_path and os.path.exists(photo_path):
            try:
                os.remove(photo_path)
            except:
                pass
                
        if avatar_path and os.path.exists(avatar_path):
            try:
                os.remove(avatar_path)
            except:
                pass
        
        # Удаляем запись из БД
        cursor.execute("DELETE FROM virt WHERE id = ?", (person_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    db.db_connect()
    # Создаем Excel-файлы для обоих каналов, если они не существуют
    services.create_excel()
    app.run(debug=True, port=5700)
