from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from gradio_client import Client, handle_file
from PIL import Image
import io, base64, tempfile, time, shutil, os, sqlite3, pandas as pd
import services, config, database as db
from database import normalize_text
from services import normalize_excel_data, create_placeholder_image
import sys
import importlib.util
from video_background_remover import quick_remove_background

# Загружаем модуль background-removal/app.py явно через spec
bg_removal_path = os.path.join(os.path.dirname(__file__), 'bg_remove', 'app.py')
spec = importlib.util.spec_from_file_location("bg_remove_app", bg_removal_path)
bg_removal_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bg_removal_app)
# Получаем функцию process из загруженного модуля
process = bg_removal_app.process

# Загружаем модуль LivePortrait/gradio_pipeline.py
LIVEPORTRAIT_PATH = os.path.join(os.path.dirname(__file__), 'LivePortrait')
sys.path.append(LIVEPORTRAIT_PATH)

try:
    from LivePortrait.src.gradio_pipeline import GradioPipeline
    from LivePortrait.src.config.crop_config import CropConfig
    from LivePortrait.src.config.argument_config import ArgumentConfig
    from LivePortrait.src.config.inference_config import InferenceConfig
    
    # Инициализируем LivePortrait pipeline
    args = ArgumentConfig()
    inference_cfg = InferenceConfig()
    crop_cfg = CropConfig()
    
    gradio_pipeline = GradioPipeline(
        inference_cfg=inference_cfg,
        crop_cfg=crop_cfg,
        args=args
    )
    LIVEPORTRAIT_AVAILABLE = True
    print("LivePortrait модуль загружен успешно")
except ImportError as e:
    LIVEPORTRAIT_AVAILABLE = False
    print(f"Ошибка загрузки LivePortrait: {e}")

app = Flask(__name__)
# Больше не нужен клиент Gradio
# client = Client("not-lain/background-removal")

UPLOAD_FOLDER = config.UPLOAD_FOLDER
PROXY_FOLDER = config.PROXY_FOLDER
BACKREMOVE_DELETED_PATH = config.BACKREMOVE_DELETED_PATH
TEMP_FOLDER = os.path.join(os.path.dirname(__file__), 'temp')
TEMP_ANIMATE_FOLDER = os.path.join(os.path.dirname(__file__), 'temp_animate')
TEMP_ANIMATE_RESULTS = os.path.join(os.path.dirname(__file__), 'temp_animate_results')

# Константы для путей
EXAMPLES_VIDEO_DIR = r"D:\Cursor projects\VirtualStudio\LivePortrait\assets\examples\driving"
FINAL_VIDEO_DIR = r"G:\Clips\animlica"

# Создаем необходимые папки при импорте
for folder in [TEMP_FOLDER, TEMP_ANIMATE_FOLDER, TEMP_ANIMATE_RESULTS, FINAL_VIDEO_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        print(f"Создана папка: {folder}")

# Создаем заглушки при запуске приложения, если их нет
def init_placeholder_images():
    create_placeholder_image("Favicon", "favicon.png", size=(32, 32))
    create_placeholder_image("РЕН ТВ", "rentv_logo.png", size=(100, 100))
    create_placeholder_image("5 КАНАЛ", "5tv_logo.png", size=(100, 100))
    create_placeholder_image("ГЛАВНОЕ", "glavnoe_logo.png", size=(100, 100))

# Инициализация заглушек при запуске
init_placeholder_images()

# Создаем папку temp_animate при запуске, если её нет
if not os.path.exists(TEMP_ANIMATE_FOLDER):
    os.makedirs(TEMP_ANIMATE_FOLDER, exist_ok=True)

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
        return jsonify({'success': False, 'error': str(e)}), 500


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

@app.route('/glavnoe')
def glavnoe():
    return render_template('glavnoe.html')

@app.route('/glavnoe_save_image', methods=['POST'])
def glavnoe_save_image():
    try:
        data = request.get_json()
        image_data = data['image']
        video_name = data['video_name']
        
        # Декодируем изображение из base64
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png', dir=TEMP_ANIMATE_FOLDER) as temp_file:
            temp_file.write(image_bytes)
            temp_file_path = temp_file.name
        
        return jsonify({
            'success': True, 
            'file_path': temp_file_path
        })
    except Exception as e:
        print(f"Ошибка при сохранении изображения: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/glavnoe_delete_image', methods=['POST'])
def glavnoe_delete_image():
    try:
        data = request.get_json()
        file_path = data['file_path']
        comment = data.get('comment', '')
        
        # Удаляем файл
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Файл удален: {file_path}")
            if comment:
                print(f"Комментарий: {comment}")
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Ошибка при удалении файла: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/glavnoe_continue_processing', methods=['POST'])
def glavnoe_continue_processing():
    try:
        data = request.get_json()
        file_path = data['file_path']
        video_name = data['video_name']
        
        # Просто сохраняем файл во временной папке (он уже там)
        # Можно добавить дополнительную логику, если нужно
        
        return jsonify({
            'success': True,
            'temp_path': file_path
        })
    except Exception as e:
        print(f"Ошибка при обработке: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/glavnoe_animate')
def glavnoe_animate():
    """Страница создания анимации"""
    file_path = request.args.get('file_path', '')
    video_name = request.args.get('video_name', 'animation')
    
    if not file_path or not os.path.exists(file_path):
        return redirect(url_for('glavnoe'))
    
    return render_template('glavnoe_animate.html', 
                         file_path=file_path, 
                         video_name=video_name)

@app.route('/get_example_videos')
def get_example_videos():
    """Получает список примеров видео из папки driving"""
    try:
        videos = []
        if os.path.exists(EXAMPLES_VIDEO_DIR):
            for filename in os.listdir(EXAMPLES_VIDEO_DIR):
                if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                    video_path = os.path.join(EXAMPLES_VIDEO_DIR, filename)
                    video_url = f"/example_video/{filename}"
                    videos.append({
                        'name': os.path.splitext(filename)[0],
                        'path': video_path,
                        'url': video_url
                    })
        
        return jsonify({
            'success': True,
            'videos': videos
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/example_video/<filename>')
def serve_example_video(filename):
    """Отдает пример видео"""
    try:
        return send_file(os.path.join(EXAMPLES_VIDEO_DIR, filename))
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/get_temp_image', methods=['POST'])
def get_temp_image():
    """Получает временное изображение"""
    try:
        data = request.get_json()
        file_path = data['file_path']
        
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return jsonify({'error': 'Файл не найден'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload_custom_video', methods=['POST'])
def upload_custom_video():
    """Загружает пользовательское видео"""
    try:
        if 'video' not in request.files:
            return jsonify({'success': False, 'error': 'Видео не выбрано'})
        
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'success': False, 'error': 'Видео не выбрано'})
        
        # Проверяем формат
        allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        file_ext = os.path.splitext(video_file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'success': False, 'error': 'Неподдерживаемый формат видео'})
        
        # Сохраняем файл
        filename = f"custom_video_{int(time.time())}{file_ext}"
        video_path = os.path.join(TEMP_ANIMATE_FOLDER, filename)
        video_file.save(video_path)
        
        return jsonify({
            'success': True,
            'video_path': video_path,
            'video_url': f'/temp_video/{filename}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/temp_video/<filename>')
def serve_temp_video(filename):
    """Отдает временное видео"""
    try:
        return send_file(os.path.join(TEMP_ANIMATE_FOLDER, filename))
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/create_animation', methods=['POST'])
def create_animation():
    """Создает анимацию используя LivePortrait"""
    try:
        if not LIVEPORTRAIT_AVAILABLE:
            return jsonify({'success': False, 'error': 'LivePortrait не доступен'})
        
        data = request.get_json()
        source_image_path = data['source_image_path']
        driving_video_path = data['driving_video_path']
        video_name = data.get('video_name', 'animation')
        
        # Проверяем существование файлов
        if not os.path.exists(source_image_path):
            return jsonify({'success': False, 'error': 'Исходное изображение не найдено'})
        
        if not os.path.exists(driving_video_path):
            return jsonify({'success': False, 'error': 'Референсное видео не найдено'})
        
        # Создаем выходной файл
        timestamp = int(time.time())
        output_filename = f"{video_name}_animated_{timestamp}.mp4"
        output_path = os.path.join(TEMP_ANIMATE_RESULTS, output_filename)
        
        # Вызываем функцию создания анимации
        result = gradio_pipeline.execute_video(
            input_image_path=source_image_path,
            input_video_path=driving_video_path,
            flag_relative_input=True,
            flag_do_crop_input=True,
            flag_remap_input=True,
            flag_crop_driving_video_input=True,
            scale=2.3,
            vx_ratio=0.0,
            vy_ratio=-0.125,
            scale_crop_driving_video=2.2,
            vx_ratio_crop_driving_video=0.0,
            vy_ratio_crop_driving_video=-0.1,
            driving_smooth_observation_variance=3e-7,
            tab_selection='Image',
            v_tab_selection='Video'
        )
        
        if result and len(result) > 0 and result[0] is not None:
            # Перемещаем результат в нашу папку
            if os.path.exists(result[0]):
                shutil.move(result[0], output_path)
                
                return jsonify({
                    'success': True,
                    'result_path': output_path,
                    'result_url': f'/temp_result/{output_filename}'
                })
            else:
                return jsonify({'success': False, 'error': 'Файл результата не создан'})
        else:
            return jsonify({'success': False, 'error': 'Ошибка создания анимации'})
            
    except Exception as e:
        print(f"Ошибка создания анимации: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/temp_result/<filename>')
def serve_temp_result(filename):
    """Отдает временный результат"""
    try:
        return send_file(os.path.join(TEMP_ANIMATE_RESULTS, filename))
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/remove_video_background', methods=['POST'])
def remove_video_background():
    """Удаляет фон с видео используя новый модуль"""
    try:
        data = request.get_json()
        input_video_path = data['video_path']
        video_name = data.get('video_name', 'processed')
        
        if not os.path.exists(input_video_path):
            return jsonify({'success': False, 'error': 'Видео не найдено'})
        
        # Обрабатываем видео
        result_path = quick_remove_background(input_video_path, video_name)
        
        if result_path and os.path.exists(result_path):
            # Создаем URL для результата
            result_filename = os.path.basename(result_path)
            result_url = f'/temp_result/{result_filename}'
            
            return jsonify({
                'success': True,
                'result_path': result_path,
                'result_url': result_url
            })
        else:
            return jsonify({'success': False, 'error': 'Ошибка удаления фона'})
            
    except Exception as e:
        print(f"Ошибка удаления фона: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/save_final_video', methods=['POST'])
def save_final_video():
    """Сохраняет финальное видео в папку назначения"""
    try:
        data = request.get_json()
        video_path = data['video_path']
        video_name = data['video_name']
        
        if not os.path.exists(video_path):
            return jsonify({'success': False, 'error': 'Видео не найдено'})
        
        # Создаем финальный путь
        file_extension = os.path.splitext(video_path)[1]
        final_filename = f"{video_name}{file_extension}"
        final_path = os.path.join(FINAL_VIDEO_DIR, final_filename)
        
        # Копируем файл
        shutil.copy2(video_path, final_path)
        
        # Удаляем временный файл
        try:
            os.remove(video_path)
        except:
            pass
        
        return jsonify({
            'success': True,
            'final_path': final_path
        })
        
    except Exception as e:
        print(f"Ошибка сохранения видео: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/delete_temp_result', methods=['POST'])
def delete_temp_result():
    """Удаляет временный результат"""
    try:
        data = request.get_json()
        file_path = data['file_path']
        
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Инициализация папок при запуске (дублируем для надежности)
    paths_to_create = [
        TEMP_FOLDER,
        TEMP_ANIMATE_FOLDER,
        TEMP_ANIMATE_RESULTS,
        FINAL_VIDEO_DIR
    ]
    
    for path in paths_to_create:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            print(f"Создана директория: {path}")

    # Проверяем доступность LivePortrait
    if not LIVEPORTRAIT_AVAILABLE:
        print("ВНИМАНИЕ: LivePortrait не доступен. Функция анимации будет отключена.")
    
    # Создаем директории для РЕН-ТВ из CHANNEL_DIRS
    for path in config.CHANNEL_DIRS['RENTV']:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            print(f"Создана директория для РЕН-ТВ: {path}")
    
    # Создаем директории для Пятого канала из CHANNEL_DIRS
    for path in config.CHANNEL_DIRS['5TV']:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            print(f"Создана директория для Пятого канала: {path}")
    
    app.run(debug=True, host='0.0.0.0', port=5500)
