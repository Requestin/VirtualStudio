import os  # Импортируем модуль os для работы с файловой системой
import time  # Импортируем модуль time для работы с задержками
import pandas as pd  # Импортируем pandas для работы с Excel файлами
from PIL import Image  # Импортируем Image из библиотеки Pillow для работы с изображениями
from threading import Thread  # Импортируем Thread из модуля threading для работы с потоками
from queue import Queue  # Импортируем Queue из модуля queue для работы с очередями

# Путь к папке с изображениями и Excel файлу
folder_path = "G:\\!PORTRETY_DATABASE"  # Путь к папке с изображениями
avatar_folder = os.path.join(folder_path, "AVATARS")  # Путь к папке с аватарками
excel_file = "G:\\!PORTRETY_DATABASE\\excel.xlsx"  # Путь к Excel файлу

# Очередь для файлов, которые нужно повторно попытаться удалить
delete_queue = Queue()  # Создаем очередь для файлов, которые нужно повторно попытаться удалить

# Переменная для хранения состояния папки
previous_files = set()

# Функция для чтения Excel файла
def read_excel_file():
    if not os.path.exists(excel_file):  # Проверяем, существует ли Excel файл
        df = pd.DataFrame(columns=["ФИО", "ДОЛЖНОСТЬ", "Путь к файлу", "Путь к аватарке"])  # Создаем DataFrame с нужными столбцами
        df.to_excel(excel_file, index=False)  # Сохраняем DataFrame в Excel файл
    else:
        df = pd.read_excel(excel_file)  # Читаем существующий Excel файл
        if set(df.columns) != {"ФИО", "ДОЛЖНОСТЬ", "Путь к файлу", "Путь к аватарке"}:  # Проверяем, что столбцы корректны
            df = pd.DataFrame(columns=["ФИО", "ДОЛЖНОСТЬ", "Путь к файлу", "Путь к аватарке"])  # Создаем DataFrame с нужными столбцами
            df.to_excel(excel_file, index=False)  # Сохраняем DataFrame в Excel файл
    return df  # Возвращаем DataFrame

# Функция для обрезки и сжатия изображения
def resize_and_compress_image(input_path, output_path, size=(300, 375), max_kb=100, bg_color=(0, 37, 76)):
    with Image.open(input_path) as img:  # Открываем изображение
        img = img.resize(size, Image.LANCZOS)  # Изменяем размер изображения с использованием высококачественного фильтра
        
        if img.mode == 'RGBA':  # Проверяем наличие альфа-канала
            background = Image.new('RGBA', img.size, bg_color + (255,))  # Создаем фон с указанным цветом
            img = Image.alpha_composite(background, img).convert('RGB')  # Накладываем изображение на фон и конвертируем в RGB
        else:
            img = img.convert('RGB')  # Конвертируем изображение в RGB, если нет альфа-канала

        img.save(output_path, format='JPEG', quality=95)  # Сохраняем изображение в формате JPEG с качеством 95
        
        while os.path.getsize(output_path) > max_kb * 1024:  # Проверяем размер файла и корректируем качество
            quality = max(1, int(95 * (max_kb * 1024) / os.path.getsize(output_path)))  # Вычисляем новое качество
            img.save(output_path, format='JPEG', quality=quality)  # Сохраняем изображение с новым качеством

# Функция для синхронизации Excel файла с папкой
def sync_with_folder():
    df = read_excel_file()  # Читаем Excel файл
    current_files = {f for f in os.listdir(folder_path) if f.endswith(".png")}  # Получаем текущие файлы в папке
    recorded_files = set(df["Путь к файлу"].apply(lambda x: os.path.basename(x)))  # Получаем файлы, записанные в Excel

    new_files = current_files - recorded_files  # Определяем новые файлы
    new_rows = []  # Создаем список для новых строк
    os.makedirs(avatar_folder, exist_ok=True)  # Создаем папку для аватаров, если она не существует

    for file in new_files:  # Обрабатываем новые файлы
        if " = " in file:  # Проверяем, что файл соответствует шаблону
            fio, position = file.rsplit(" = ", 1)  # Разделяем ФИО и должность
            position = position.replace(".png", "")  # Убираем расширение из должности
            file_path = os.path.join(folder_path, file)  # Формируем полный путь к файлу
            avatar_path = os.path.join(avatar_folder, file.replace('.png', '.jpg'))  # Формируем путь к аватару
            
            resize_and_compress_image(file_path, avatar_path)  # Обрезаем и сжимаем изображение

            new_rows.append({"ФИО": fio, "ДОЛЖНОСТЬ": position, "Путь к файлу": file_path, "Путь к аватарке": avatar_path})  # Добавляем новую строку в список
    
    if new_rows:  # Если есть новые строки
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)  # Объединяем новые строки с текущим DataFrame

    missing_files = recorded_files - current_files  # Определяем отсутствующие файлы
    df = df[~df["Путь к файлу"].apply(lambda x: os.path.basename(x)).isin(missing_files)]  # Убираем строки с отсутствующими файлами

    for file in missing_files:  # Обрабатываем отсутствующие файлы
        avatar_path = os.path.join(avatar_folder, file.replace('.png', '.jpg'))  # Формируем путь к аватару
        delete_queue.put(avatar_path)  # Добавляем файл в очередь на удаление

    df = df.sort_values(by="ФИО").reset_index(drop=True)  # Сортируем DataFrame по ФИО и сбрасываем индекс

    save_excel_file(df)  # Сохраняем Excel файл

# Функция для сохранения Excel файла
def save_excel_file(df, max_retries=10):
    retries = 0  # Счетчик попыток сохранения
    while retries < max_retries:  # Пока не превышено максимальное количество попыток
        try:
            df.to_excel(excel_file, index=False)  # Пытаемся сохранить DataFrame в Excel файл
            break  # Если удалось сохранить, выходим из цикла
        except PermissionError:  # Если возникла ошибка доступа
            retries += 1  # Увеличиваем счетчик попыток
            print(f"Permission denied: '{excel_file}'. Retrying in 5 seconds... ({retries}/{max_retries})")  # Сообщаем о повторной попытке
            time.sleep(5)  # Ждем 5 секунд перед повторной попыткой
    else:
        print(f"Failed to save the file after {max_retries} attempts. Please close the file if it's open and try again.")  # Сообщаем об ошибке после всех попыток

# Функция-поток для повторных попыток удаления файлов
def delete_file_worker():
    while True:  # Бесконечный цикл
        file_path = delete_queue.get()  # Получаем файл из очереди
        while True:  # Пытаемся удалить файл, пока не удастся
            try:
                if os.path.exists(file_path):  # Проверяем, существует ли файл
                    os.remove(file_path)  # Удаляем файл
                    print(f"Successfully deleted: {file_path}")  # Сообщаем об успешном удалении
                break  # Выходим из внутреннего цикла
            except PermissionError:  # Если возникла ошибка доступа
                print(f"Permission denied: '{file_path}'. Retrying in 5 seconds...")  # Сообщаем о повторной попытке
                time.sleep(5)  # Ждем 5 секунд перед повторной попыткой
        delete_queue.task_done()  # Сообщаем очереди, что задача выполнена

# Функция для проверки изменений в папке
def check_for_changes():
    global previous_files
    current_files = {f for f in os.listdir(folder_path) if f.endswith(".png")}  # Получаем текущие файлы в папке
    if current_files != previous_files:
        previous_files = current_files
        sync_with_folder()  # Синхронизируем папку при изменениях

# Функция для запуска мониторинга изменений в папке
def start_monitoring():
    while True:
        check_for_changes()  # Проверяем изменения в папке
        time.sleep(1)  # Ждем 1 секунду перед следующей проверкой

# Запускаем поток для удаления файлов
delete_worker_thread = Thread(target=delete_file_worker, daemon=True)  # Создаем поток для удаления файлов
delete_worker_thread.start()  # Запускаем поток

# Запускаем поток для мониторинга изменений в папке
monitor_thread = Thread(target=start_monitoring, daemon=True)  # Создаем поток для мониторинга изменений
monitor_thread.start()  # Запускаем поток

# Основной поток ждет завершения мониторинга (теоретически бесконечно)
monitor_thread.join()  # Ждем завершения потока мониторинга
