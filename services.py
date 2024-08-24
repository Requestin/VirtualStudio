import pandas as pd
import os
from app import EXCEL_FILE

def create_excel():
    if not os.path.exists(EXCEL_FILE):
        data = {
        '2 окна ФИО': [''],
        '2 окна ДОЛЖНОСТЬ': [''],
        '2 окна ПУТЬ': [''],
        }

        # Создаем DataFrame
        df = pd.DataFrame(data)

        # Путь к файлу Excel
        excel_file = 'data/data.xlsx'

        # Сохраняем DataFrame в Excel
        df.to_excel(excel_file, index=False)

        print(f"Файл {excel_file} успешно создан.")
    else:
        print(f'Файл {EXCEL_FILE} уже существует!')