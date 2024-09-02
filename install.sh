#!/bin/bash

# Функция для создания директорий
create_directories() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        mkdir -p data\proxy data\uploads
    else
        mkdir -p data/proxy data/uploads
    fi
}

# Функция для создания и активации виртуального окружения
create_and_activate_venv() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        python -m venv venv
        source venv/Scripts/activate
    else
        python3 -m venv venv
        source venv/bin/activate
    fi
}

# Создание папок
create_directories

# Создание и активация виртуального окружения
create_and_activate_venv

# Установка зависимостей
pip install -r requirements.txt

echo "Установка завершена успешно!"
