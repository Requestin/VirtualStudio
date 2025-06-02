import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

def setup_logger():
    """
    Настройка системы логгирования для VirtualStudio
    Логи ротируются ежемесячно, старые файлы автоматически удаляются
    """
    # Создаем папку для логов, если она не существует
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Настройка основного логгера
    logger = logging.getLogger('VirtualStudio')
    logger.setLevel(logging.INFO)
    
    # Очищаем существующие обработчики
    if logger.handlers:
        logger.handlers.clear()
    
    # Формат логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Обработчик для записи в файл с ротацией по времени (каждый месяц, хранить 12 месяцев)
    log_file = os.path.join(log_dir, 'virtualstudio.log')
    file_handler = TimedRotatingFileHandler(
        log_file,
        when='midnight',        # Ротация в полночь
        interval=30,            # Каждые 30 дней (примерно месяц)
        backupCount=12,         # Хранить 12 файлов (год)
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    # Добавляем суффикс с датой к ротированным файлам
    file_handler.suffix = "%Y-%m"
    
    # Обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Создаем отдельный логгер для операций с файлами
    file_logger = logging.getLogger('VirtualStudio.FileOperations')
    file_logger.setLevel(logging.INFO)
    
    # Отдельный файл для операций с файлами (ротация каждые 2 недели, хранить 6 месяцев)
    file_ops_log = os.path.join(log_dir, 'file_operations.log')
    file_ops_handler = TimedRotatingFileHandler(
        file_ops_log,
        when='midnight',
        interval=14,            # Каждые 14 дней
        backupCount=12,         # Хранить 12 файлов (~6 месяцев)
        encoding='utf-8'
    )
    file_ops_handler.setLevel(logging.INFO)
    file_ops_handler.setFormatter(formatter)
    file_ops_handler.suffix = "%Y-%m-%d"
    file_logger.addHandler(file_ops_handler)
    
    # Создаем отдельный логгер для операций с базой данных
    db_logger = logging.getLogger('VirtualStudio.Database')
    db_logger.setLevel(logging.INFO)
    
    # Отдельный файл для операций с БД (ротация каждые 2 недели, хранить 6 месяцев)
    db_log = os.path.join(log_dir, 'database.log')
    db_handler = TimedRotatingFileHandler(
        db_log,
        when='midnight',
        interval=14,            # Каждые 14 дней  
        backupCount=12,         # Хранить 12 файлов (~6 месяцев)
        encoding='utf-8'
    )
    db_handler.setLevel(logging.INFO)
    db_handler.setFormatter(formatter)
    db_handler.suffix = "%Y-%m-%d"
    db_logger.addHandler(db_handler)
    
    # Логгируем успешную инициализацию
    logger.info("Система логгирования VirtualStudio инициализирована")
    logger.info(f"Логи сохраняются в директории: {os.path.abspath(log_dir)}")
    logger.info("Ротация логов: основной - каждый месяц (12 месяцев), операции - каждые 2 недели (6 месяцев)")
    
    return logger

def get_logger(name='VirtualStudio'):
    """
    Получить логгер по имени
    """
    return logging.getLogger(name)

def cleanup_old_logs():
    """
    Функция для ручной очистки старых логов (если потребуется)
    Удаляет все .log файлы старше 1 года
    """
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        return
    
    import time
    current_time = time.time()
    one_year_ago = current_time - (365 * 24 * 60 * 60)  # 365 дней в секундах
    
    deleted_files = []
    
    for filename in os.listdir(log_dir):
        if filename.endswith('.log') and not filename.startswith('virtualstudio.log'):
            # Проверяем файлы с суффиксами дат
            file_path = os.path.join(log_dir, filename)
            file_time = os.path.getctime(file_path)
            
            if file_time < one_year_ago:
                try:
                    os.remove(file_path)
                    deleted_files.append(filename)
                except Exception as e:
                    logger = get_logger()
                    logger.error(f"Ошибка при удалении старого лог-файла {filename}: {e}")
    
    if deleted_files:
        logger = get_logger()
        logger.info(f"Удалены старые лог-файлы: {', '.join(deleted_files)}")

# Автоматическая инициализация при импорте
main_logger = setup_logger() 