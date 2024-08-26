import os
from flask import Flask, request, jsonify, render_template
from gradio_client import Client, handle_file
from PIL import Image
import io
import base64
import tempfile
import time

app = Flask(__name__)

# Инициализация клиента Gradio
client = Client("not-lain/background-removal")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_image', methods=['POST'])
def save_image():
    if 'image' not in request.json:
        return jsonify({'success': False, 'error': 'No image data'}), 400
    
    image_data = base64.b64decode(request.json['image'].split(',')[1])
    name = request.json['name']
    position = request.json['position']
    
    # Создаем объект изображения из полученных данных
    img = Image.open(io.BytesIO(image_data))
    
    try:
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            img.save(temp_file, format='PNG')
            temp_file_path = temp_file.name
        
        # Отправляем изображение на обработку с повторными попытками
        max_retries = 3
        for attempt in range(max_retries):
            try:
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
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        # Формируем имя файла из введенных данных
        base_filename = f"{name} = {position}.png"
        final_file_path = os.path.join(save_path, base_filename)
        
        # Проверяем, существует ли файл с таким именем
        counter = 1
        while os.path.exists(final_file_path):
            filename_parts = os.path.splitext(base_filename)
            final_file_path = os.path.join(save_path, f"{filename_parts[0]}_{counter}{filename_parts[1]}")
            counter += 1
        
        # Копируем обработанное изображение в финальную папку
        with Image.open(output_image_path) as img:
            img.save(final_file_path, "PNG")
        
        # Удаляем временные файлы
        os.remove(temp_file_path)
        os.remove(output_image_path)
        
        return jsonify({'success': True, 'file_path': final_file_path})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        # Убеждаемся, что временный файл удален в любом случае
        if 'temp_file_path' in locals():
            try:
                os.remove(temp_file_path)
            except:
                pass

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)