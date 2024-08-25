import pandas as pd
import os
import config
from PIL import Image


def create_excel():
    if not os.path.exists(config.EXCEL_FILE):
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
        }

        # Создаем DataFrame
        df = pd.DataFrame(data)

        # Путь к файлу Excel
        excel_file = 'data/data.xlsx'

        # Сохраняем DataFrame в Excel
        df.to_excel(excel_file, index=False)

        print(f"Файл {excel_file} успешно создан.")
    else:
        print(f'Файл {config.EXCEL_FILE} уже существует!')


def update_excel(module_name, fio, position, filepath, proxy_filepath, i):
    df = pd.read_excel(config.EXCEL_FILE)
    fio_col = f'{module_name} ФИО {i}'
    position_col = f'{module_name} ДОЛЖНОСТЬ {i}'
    path_col = f'{module_name} ПУТЬ {i}'
    avatar_col = f'{module_name} АВАТАР {i}'

    df.at[0, fio_col] = fio
    df.at[0, position_col] = position
    df.at[0, path_col] = filepath
    df.at[0, avatar_col] = proxy_filepath

    df.to_excel(config.EXCEL_FILE, index = False)


def convert_for_avatar(image_path, output_path, size=(300, 375), max_size_kb=49):
    try:
        with Image.open(image_path) as img:
            # Изменение размера изображения
            img = img.resize(size, Image.LANCZOS)

            # Начальное сохранение с качеством 95 в формате JPEG
            quality = 95
            img.save(output_path, format='JPEG', quality=quality, optimize=True)

            # Проверка размера файла и уменьшение качества, если необходимо
            last_size = os.path.getsize(output_path)
            while last_size > max_size_kb * 1024 and quality > 10:
                quality -= 5  # Уменьшаем качество на 5%

                # Повторное сохранение с новым качеством
                img.save(output_path, format='JPEG', quality=quality, optimize=True)

                current_size = os.path.getsize(output_path)
                if current_size >= last_size:
                    # Если размер файла не уменьшается, прекращаем цикл
                    print("Дальнейшее уменьшение качества не влияет на размер файла.")
                    break

                last_size = current_size

            final_size_kb = os.path.getsize(output_path) / 1024
            print(f"Финальный размер изображения: {final_size_kb:.2f} КБ, с качеством: {quality}")

    except Exception as e:
        print(f"Ошибка обработки изображения: {e}")
        raise



# def convert_for_avatar(image_path, output_path, size=(300, 375), max_size_kb = 49):
#     try:
#         with Image.open(image_path) as img:
#             img = img.resize(size, Image.LANCZOS)
#             img.save(output_path, format='PNG', optimize=True)

#         while os.path.getsize(output_path) > max_size_kb * 1024:
#             quality = max(10, int(100 * (max_size_kb * 1024 / os.path.getsize(output_path))))
#             img.save(output_path, format='PNG', quality=quality, optimize=True)
#     except Exception as e:
#         print(f'Ошибка {e}')
#         raise

