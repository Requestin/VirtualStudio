# Создание папок, если они не существуют
if (!(Test-Path ".\data\proxy")) {
    New-Item -ItemType Directory -Force -Path ".\data\proxy"
}
if (!(Test-Path ".\data\uploads")) {
    New-Item -ItemType Directory -Force -Path ".\data\uploads"
}

# Создание виртуального окружения, если оно не существует
if (!(Test-Path ".\venv")) {
    python -m venv venv
}

# Активация виртуального окружения
.\venv\Scripts\Activate.ps1

# Установка зависимостей из requirements.txt
pip install -r requirements.txt
