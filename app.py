from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from gradio_client import Client, handle_file
from PIL import Image
import io, base64, tempfile, time, shutil, os, sqlite3, pandas as pd
import services, config, database as db
from database import normalize_text
from services import normalize_excel_data, create_placeholder_image
import sys
import importlib.util

# Загружаем модуль background-removal/app.py явно через spec
bg_removal_path = os.path.join(os.path.dirname(__file__), 'bg_remove', 'app.py')
spec = importlib.util.spec_from_file_location("bg_remove_app", bg_removal_path)
bg_removal_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bg_removal_app)
# Получаем функцию process из загруженного модуля
process = bg_removal_app.process

app = Flask(__name__)
# Больше не нужен клиент Gradio
# client = Client("not-lain/background-removal")

UPLOAD_FOLDER = config.UPLOAD_FOLDER
PROXY_FOLDER = config.PROXY_FOLDER
BACKREMOVE_DELETED_PATH = config.BACKREMOVE_DELETED_PATH

# Создаем заглушки при запуске приложения, если их нет
def init_placeholder_images():
    create_placeholder_image("Favicon", "favicon.png", size=(32, 32))
    create_placeholder_image("РЕН ТВ", "rentv_logo.png", size=(100, 100))
    create_placeholder_image("5 КАНАЛ", "5tv_logo.png", size=(100, 100))

# Инициализация заглушек при запуске
init_placeholder_images()

# Функция для дублирования файла из одного канала в другой
def duplicate_to_other_channel(file_path):
    """
    Дублирует файл из директории одного канала в директорию другого канала,
    или из общей директории в директории обоих каналов
    
    :param file_path: Полный путь к файлу
    """
    if not file_path:
        return
        
    try:
        # Получаем имя файла
        filename = os.path.basename(file_path)
        
        # Определяем папку с файлом
        file_dir = os.path.dirname(file_path)
        
        # Если файл в папке RENTV, копируем в 5TV
        if 'RENTV' in file_dir:
            # Определяем тип файла
            file_type = 'upload'
            if 'AVATARS' in file_dir:
                file_type = 'proxy'
            elif 'DELETED' in file_dir:
                file_type = 'deleted'
                
            # Получаем соответствующий путь для 5TV
            target_dir = config.get_channel_path(file_type, '5tv')
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, filename)
            shutil.copy2(file_path, target_path)
            print(f"Файл скопирован из {file_path} в {target_path}")
            
        # Если файл в папке 5TV, копируем в RENTV
        elif '5TV' in file_dir:
            # Определяем тип файла
            file_type = 'upload'
            if 'AVATARS' in file_dir:
                file_type = 'proxy'
            elif 'DELETED' in file_dir:
                file_type = 'deleted'
                
            # Получаем соответствующий путь для RENTV
            target_dir = config.get_channel_path(file_type, 'rentv')
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, filename)
            shutil.copy2(file_path, target_path)
            print(f"Файл скопирован из {file_path} в {target_path}")
            
        # Если файл в общей директории, копируем в директорию 5TV (RENTV уже использует общие директории)
        else:
            # Определяем тип файла
            file_type = 'upload'
            if 'AVATARS' in file_dir or 'proxy_' in filename:
                file_type = 'proxy'
            elif 'DELETED' in file_dir:
                file_type = 'deleted'
            
            # Копируем только в 5TV, так как общие пути уже используются для RENTV
            # Получаем соответствующий путь для 5TV
            target_dir = config.get_channel_path(file_type, '5tv')
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, filename)
            shutil.copy2(file_path, target_path)
            print(f"Файл скопирован из {file_path} в {target_path}")
    except Exception as e:
        print(f"Ошибка при дублировании файла: {e}")

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
        fio = normalize_text(request.form['fio'])
        position = normalize_text(request.form['position'])
        file = request.files['photo']

        if fio and position and file and services.allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            proxy_filename = f'proxy_{filename}'
            proxy_filepath = os.path.join(PROXY_FOLDER, proxy_filename)
            services.convert_for_avatar(filepath, proxy_filepath)
            db.db_add_new_person(fio, position, filepath, proxy_filepath)
            
            # Дублируем файлы в другой канал
            duplicate_to_other_channel(filepath)
            duplicate_to_other_channel(proxy_filepath)
            
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
            fio = normalize_text(request.form[f'fio{i}'])
            position = normalize_text(request.form[f'position{i}'])
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i, channel)
    # Чтение данных из Excel
    excel_file = config.CHANNELS[channel]['excel']
    df = pd.read_excel(excel_file)
    # Нормализуем данные из Excel
    df = normalize_excel_data(df)
    data = df.to_dict('list')
    channel_name = config.CHANNELS[channel]['name']
    return render_template('1win_v1.html', data=data, module_name=module_name, channel=channel, channel_name=channel_name)


@app.route('/<channel>/1win_v2', methods=['GET', 'POST'])
def module_1win_v2(channel):
    if channel not in config.CHANNELS:
        return redirect(url_for('index'))
        
    module_name = '1win_v2'
    if request.method == 'POST':
        for i in range(1, 2):
            fio = normalize_text(request.form[f'fio{i}'])
            position = normalize_text(request.form[f'position{i}'])
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i, channel)
    # Чтение данных из Excel
    excel_file = config.CHANNELS[channel]['excel']
    df = pd.read_excel(excel_file)
    # Нормализуем данные из Excel
    df = normalize_excel_data(df)
    data = df.to_dict('list')
    channel_name = config.CHANNELS[channel]['name']
    return render_template('1win_v2.html', data=data, module_name=module_name, channel=channel, channel_name=channel_name)

@app.route('/<channel>/1win_v3', methods=['GET', 'POST'])
def module_1win_v3(channel):
    if channel not in config.CHANNELS:
        return redirect(url_for('index'))
        
    module_name = '1win_v3'
    if request.method == 'POST':
        for i in range(1, 2):
            fio = normalize_text(request.form[f'fio{i}'])
            position = normalize_text(request.form[f'position{i}'])
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i, channel)
    # Чтение данных из Excel
    excel_file = config.CHANNELS[channel]['excel']
    df = pd.read_excel(excel_file)
    # Нормализуем данные из Excel
    df = normalize_excel_data(df)
    data = df.to_dict('list')
    channel_name = config.CHANNELS[channel]['name']
    return render_template('1win_v3.html', data=data, module_name=module_name, channel=channel, channel_name=channel_name)


@app.route('/<channel>/2win_v1', methods=['GET', 'POST'])
def module_2win_v1(channel):
    if channel not in config.CHANNELS:
        return redirect(url_for('index'))
        
    module_name = '2win_v1'
    if request.method == 'POST':
        for i in range(1, 3):
            fio = normalize_text(request.form[f'fio{i}'])
            position = normalize_text(request.form[f'position{i}'])
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i, channel)
    # Чтение данных из Excel
    excel_file = config.CHANNELS[channel]['excel']
    df = pd.read_excel(excel_file)
    # Нормализуем данные из Excel
    df = normalize_excel_data(df)
    data = df.to_dict('list')
    channel_name = config.CHANNELS[channel]['name']
    return render_template('2win_v1.html', data=data, module_name=module_name, channel=channel, channel_name=channel_name)


@app.route('/<channel>/2win_v2', methods=['GET', 'POST'])
def module_2win_v2(channel):
    if channel not in config.CHANNELS:
        return redirect(url_for('index'))
        
    module_name = '2win_v2'
    if request.method == 'POST':
        for i in range(1, 3):
            fio = normalize_text(request.form[f'fio{i}'])
            position = normalize_text(request.form[f'position{i}'])
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i, channel)
    # Чтение данных из Excel
    excel_file = config.CHANNELS[channel]['excel']
    df = pd.read_excel(excel_file)
    # Нормализуем данные из Excel
    df = normalize_excel_data(df)
    data = df.to_dict('list')
    channel_name = config.CHANNELS[channel]['name']
    return render_template('2win_v2.html', data=data, module_name=module_name, channel=channel, channel_name=channel_name)


@app.route('/<channel>/2win_v3', methods=['GET', 'POST'])
def module_2win_v3(channel):
    if channel not in config.CHANNELS:
        return redirect(url_for('index'))
        
    module_name = '2win_v3'
    if request.method == 'POST':
        for i in range(1, 3):
            fio = normalize_text(request.form[f'fio{i}'])
            position = normalize_text(request.form[f'position{i}'])
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i, channel)
    # Чтение данных из Excel
    excel_file = config.CHANNELS[channel]['excel']
    df = pd.read_excel(excel_file)
    # Нормализуем данные из Excel
    df = normalize_excel_data(df)
    data = df.to_dict('list')
    channel_name = config.CHANNELS[channel]['name']
    return render_template('2win_v3.html', data=data, module_name=module_name, channel=channel, channel_name=channel_name)


@app.route('/<channel>/3win_v1', methods=['GET', 'POST'])
def module_3win_v1(channel):
    if channel not in config.CHANNELS:
        return redirect(url_for('index'))
        
    module_name = '3win_v1'
    if request.method == 'POST':
        for i in range(1, 4):
            fio = normalize_text(request.form[f'fio{i}'])
            position = normalize_text(request.form[f'position{i}'])
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i, channel)
    # Чтение данных из Excel
    excel_file = config.CHANNELS[channel]['excel']
    df = pd.read_excel(excel_file)
    # Нормализуем данные из Excel
    df = normalize_excel_data(df)
    data = df.to_dict('list')
    channel_name = config.CHANNELS[channel]['name']
    return render_template('3win_v1.html', data=data, module_name=module_name, channel=channel, channel_name=channel_name)


@app.route('/<channel>/3win_v2', methods=['GET', 'POST'])
def module_3win_v2(channel):
    if channel not in config.CHANNELS:
        return redirect(url_for('index'))
        
    module_name = '3win_v2'
    if request.method == 'POST':
        for i in range(1, 4):
            fio = normalize_text(request.form[f'fio{i}'])
            position = normalize_text(request.form[f'position{i}'])
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i, channel)
    # Чтение данных из Excel
    excel_file = config.CHANNELS[channel]['excel']
    df = pd.read_excel(excel_file)
    # Нормализуем данные из Excel
    df = normalize_excel_data(df)
    data = df.to_dict('list')
    channel_name = config.CHANNELS[channel]['name']
    return render_template('3win_v2.html', data=data, module_name=module_name, channel=channel, channel_name=channel_name)


@app.route('/<channel>/3win_v3', methods=['GET', 'POST'])
def module_3win_v3(channel):
    if channel not in config.CHANNELS:
        return redirect(url_for('index'))
        
    module_name = '3win_v3'
    if request.method == 'POST':
        for i in range(1, 4):
            fio = normalize_text(request.form[f'fio{i}'])
            position = normalize_text(request.form[f'position{i}'])
            filepath = request.form[f'photo_path{i}']
            proxy_filepath = request.form[f'proxy_path{i}']

            if fio and position and filepath and proxy_filepath:
                services.update_excel(module_name, fio, position, filepath, proxy_filepath, i, channel)
    # Чтение данных из Excel
    excel_file = config.CHANNELS[channel]['excel']
    df = pd.read_excel(excel_file)
    # Нормализуем данные из Excel
    df = normalize_excel_data(df)
    data = df.to_dict('list')
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
    # Проверяем, есть ли данные изображения в запросе
    if 'image' not in request.json:
        # Если нет, возвращаем ошибку
        return jsonify({'success': False, 'error': 'No image data'}), 400
    # Декодируем данные изображения из base64
    image_data = base64.b64decode(request.json['image'].split(',')[1])
    # Получаем имя из данных запроса и нормализуем
    name = normalize_text(request.json['name'])
    # Получаем должность из данных запроса и нормализуем
    position = normalize_text(request.json['position'])
    # Создаем объект изображения из полученных данных
    img = Image.open(io.BytesIO(image_data))
    
    try:
        # Создаем временный файл для исходного изображения
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            # Сохраняем изображение во временный файл
            img.save(temp_file, format='PNG')
            # Получаем путь к временному файлу
            temp_file_path = temp_file.name
        
        # Открываем изображение и напрямую применяем функцию process для удаления фона
        input_image = Image.open(temp_file_path).convert("RGB")
        # Используем импортированную функцию process
        output_image = process(input_image)
        
        # Сохраняем обработанное изображение во временный файл
        output_image_path = temp_file_path + "_output.png"
        output_image.save(output_image_path)
        
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
        shutil.copy(output_image_path, final_file_path)
        
        # Дублируем файл в другой канал
        duplicate_to_other_channel(final_file_path)

        # Удаляем временные файлы
        os.remove(temp_file_path)
        os.remove(output_image_path)
        
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
        # Также удаляем временный файл с результатом, если он существует
        if 'output_image_path' in locals() and os.path.exists(output_image_path):
            try:
                os.remove(output_image_path)
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
            # Определяем канал на основе пути к файлу
            channel = 'rentv'  # по умолчанию РЕН ТВ
            if '5TV' in file_path:
                channel = '5tv'
                
            deleted_path = config.get_channel_path('deleted', channel)
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
            
            # Ищем и удаляем такой же файл из другого канала
            other_channel = 'rentv' if channel == '5tv' else '5tv'
            other_channel_path = config.get_channel_path('upload', other_channel)
            other_channel_file = os.path.join(other_channel_path, base_filename)
            
            # Проверяем, существует ли файл в директории другого канала
            if not os.path.exists(other_channel_file):
                # Если не в корневой директории, проверяем в директории AVATARS
                if 'AVATARS' in file_path:
                    other_channel_path = config.get_channel_path('proxy', other_channel)
                    other_channel_file = os.path.join(other_channel_path, base_filename)
                
            if os.path.exists(other_channel_file):
                # Перемещаем файл из другого канала в его папку DELETED
                other_deleted_path = config.get_channel_path('deleted', other_channel)
                if not os.path.exists(other_deleted_path):
                    os.makedirs(other_deleted_path, exist_ok=True)
                
                other_deleted_file_path = os.path.join(other_deleted_path, base_filename)
                
                # Проверяем, существует ли файл с таким именем в папке DELETED другого канала
                counter = 1
                while os.path.exists(other_deleted_file_path):
                    filename_parts = os.path.splitext(base_filename)
                    other_deleted_file_path = os.path.join(other_deleted_path, f"{filename_parts[0]}_{counter}{filename_parts[1]}")
                    counter += 1
                
                # Перемещаем файл из другого канала
                shutil.move(other_channel_file, other_deleted_file_path)
                print(f"Файл из другого канала перемещен в DELETED: {other_deleted_file_path}")
            
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
    name = normalize_text(data.get('name'))
    position = normalize_text(data.get('position'))

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
        
        # Дублируем файлы в другой канал
        duplicate_to_other_channel(file_path)
        duplicate_to_other_channel(avatar_path)

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
    
    # Создаем директории для РЕН-ТВ, если они не существуют
    rentv_dirs = [
        config.UPLOAD_FOLDER,
        config.PROXY_FOLDER,
        config.BACKREMOVE_DELETED_PATH
    ]
    
    for path in rentv_dirs:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            print(f"Создана директория для РЕН-ТВ: {path}")
    
    # Создаем директории для Пятого канала из CHANNEL_DIRS
    for path in config.CHANNEL_DIRS['5TV']:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            print(f"Создана директория для Пятого канала: {path}")
    
    app.run(debug=True, host='0.0.0.0', port=5500)
