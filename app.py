# Импортируем модуль для работы с операционной системой
import os
# Импортируем необходимые компоненты из Flask
from flask import Flask, request, jsonify, render_template
# Импортируем клиент Gradio и функцию для обработки файлов
from gradio_client import Client, handle_file
# Импортируем модуль для работы с изображениями
from PIL import Image
# Импортируем модуль для работы с байтовыми потоками
import io
# Импортируем модуль для кодирования и декодирования в base64
import base64
# Импортируем модуль для работы с временными файлами
import tempfile
# Импортируем модуль для работы со временем
import time

# Создаем экземпляр Flask приложения
app = Flask(__name__)

# Инициализация клиента Gradio для удаления фона
client = Client("not-lain/background-removal")

# Определяем маршрут для главной страницы
@app.route('/')
def index():
    # Отображаем шаблон index.html
    return render_template('index.html')

# Определяем маршрут для сохранения изображения, принимающий POST запросы
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
        save_path = r'G:\!PORTRETY_DATABASE'
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

# Если скрипт запущен напрямую, запускаем Flask приложение
if __name__ == '__main__':
    # Запускаем сервер в режиме отладки, доступный извне, на порту 5000
    app.run(debug=True, host='0.0.0.0', port=5000)