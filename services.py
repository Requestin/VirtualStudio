import pandas as pd
import os
import config
from PIL import Image


def create_excel(channel_key=None):
    """
    Создает Excel-файл для указанного канала или для всех каналов, если канал не указан
    """
    # Определяем каналы для обработки
    channels_to_process = []
    if channel_key:
        if channel_key in config.CHANNELS:
            channels_to_process.append((channel_key, config.CHANNELS[channel_key]['excel']))
        else:
            print(f"Канал {channel_key} не найден в конфигурации")
            return
    else:
        for key, value in config.CHANNELS.items():
            channels_to_process.append((key, value['excel']))

    # Создаем Excel для каждого канала в списке
    for channel_key, excel_file in channels_to_process:
        if not os.path.exists(excel_file):
            data = {
            '3win_v1 ФИО 1': [''],
            '3win_v1 ДОЛЖНОСТЬ 1': [''],
            '3win_v1 ПУТЬ 1': [''],
            '3win_v1 АВАТАР 1': [''],

            '3win_v1 ФИО 2': [''],
            '3win_v1 ДОЛЖНОСТЬ 2': [''],
            '3win_v1 ПУТЬ 2': [''],
            '3win_v1 АВАТАР 2': [''],

            '3win_v1 ФИО 3': [''],
            '3win_v1 ДОЛЖНОСТЬ 3': [''],
            '3win_v1 ПУТЬ 3': [''],
            '3win_v1 АВАТАР 3': [''],
            #####

            '3win_v2 ФИО 1': [''],
            '3win_v2 ДОЛЖНОСТЬ 1': [''],
            '3win_v2 ПУТЬ 1': [''],
            '3win_v2 АВАТАР 1': [''],

            '3win_v2 ФИО 2': [''],
            '3win_v2 ДОЛЖНОСТЬ 2': [''],
            '3win_v2 ПУТЬ 2': [''],
            '3win_v2 АВАТАР 2': [''],
            
            '3win_v2 ФИО 3': [''],
            '3win_v2 ДОЛЖНОСТЬ 3': [''],
            '3win_v2 ПУТЬ 3': [''],
            '3win_v2 АВАТАР 3': [''],
            #####

            '3win_v3 ФИО 1': [''],
            '3win_v3 ДОЛЖНОСТЬ 1': [''],
            '3win_v3 ПУТЬ 1': [''],
            '3win_v3 АВАТАР 1': [''],
           
            '3win_v3 ФИО 2': [''],
            '3win_v3 ДОЛЖНОСТЬ 2': [''],
            '3win_v3 ПУТЬ 2': [''],
            '3win_v3 АВАТАР 2': [''],
           
            '3win_v3 ФИО 3': [''],
            '3win_v3 ДОЛЖНОСТЬ 3': [''],
            '3win_v3 ПУТЬ 3': [''],
            '3win_v3 АВАТАР 3': [''],
            #####
            
            '2win_v1 ФИО 1': [''],
            '2win_v1 ДОЛЖНОСТЬ 1': [''],
            '2win_v1 ПУТЬ 1': [''],
            '2win_v1 АВАТАР 1': [''],
            
            '2win_v1 ФИО 2': [''],
            '2win_v1 ДОЛЖНОСТЬ 2': [''],
            '2win_v1 ПУТЬ 2': [''],
            '2win_v1 АВАТАР 2': [''],
            #####

            '2win_v2 ФИО 1': [''],
            '2win_v2 ДОЛЖНОСТЬ 1': [''],
            '2win_v2 ПУТЬ 1': [''],
            '2win_v2 АВАТАР 1': [''],
            
            '2win_v2 ФИО 2': [''],
            '2win_v2 ДОЛЖНОСТЬ 2': [''],
            '2win_v2 ПУТЬ 2': [''],
            '2win_v2 АВАТАР 2': [''],
            #####

            '2win_v3 ФИО 1': [''],
            '2win_v3 ДОЛЖНОСТЬ 1': [''],
            '2win_v3 ПУТЬ 1': [''],
            '2win_v3 АВАТАР 1': [''],
            
            '2win_v3 ФИО 2': [''],
            '2win_v3 ДОЛЖНОСТЬ 2': [''],
            '2win_v3 ПУТЬ 2': [''],
            '2win_v3 АВАТАР 2': [''],
            #####

            '1win_v1 ФИО 1': [''],
            '1win_v1 ДОЛЖНОСТЬ 1': [''],
            '1win_v1 ПУТЬ 1': [''],
            '1win_v1 АВАТАР 1': [''],
            #####

            '1win_v2 ФИО 1': [''],
            '1win_v2 ДОЛЖНОСТЬ 1': [''],
            '1win_v2 ПУТЬ 1': [''],
            '1win_v2 АВАТАР 1': [''],
            #####

            '1win_v3 ФИО 1': [''],
            '1win_v3 ДОЛЖНОСТЬ 1': [''],
            '1win_v3 ПУТЬ 1': [''],
            '1win_v3 АВАТАР 1': [''],
            #####
            }

            # Создаем DataFrame
            df = pd.DataFrame(data)

            # Проверяем наличие директории
            directory = os.path.dirname(excel_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            # Сохраняем DataFrame в Excel
            df.to_excel(excel_file, index=False)

            print(f"Файл {excel_file} успешно создан.")
        else:
            print(f'Файл {excel_file} уже существует!')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


def update_excel(module_name, fio, position, filepath, proxy_filepath, i, channel):
    # Получаем путь к Excel-файлу для выбранного телеканала
    if channel in config.CHANNELS:
        excel_file = config.CHANNELS[channel]['excel']
    else:
        print(f"Ошибка: канал {channel} не найден")
        return
    
    df = pd.read_excel(excel_file)
    fio_col = f'{module_name} ФИО {i}'
    position_col = f'{module_name} ДОЛЖНОСТЬ {i}'
    path_col = f'{module_name} ПУТЬ {i}'
    avatar_col = f'{module_name} АВАТАР {i}'

    df.at[0, fio_col] = fio
    df.at[0, position_col] = position
    df.at[0, path_col] = filepath
    df.at[0, avatar_col] = proxy_filepath

    df.to_excel(excel_file, index = False)


def convert_for_avatar(input_path, output_path, size=(300, 375), max_kb=100, bg_color=(0, 37, 76)):
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

