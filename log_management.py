#!/usr/bin/env python3
"""
Скрипт управления логами VirtualStudio
Предоставляет утилиты для мониторинга, анализа и очистки файлов логов
"""

import os
import time
import glob
from datetime import datetime, timedelta
from logger_config import cleanup_old_logs, get_logger

def show_log_stats():
    """Показывает статистику файлов логов"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        print("❌ Папка логов не найдена")
        return
    
    print("📊 Статистика файлов логов:")
    print("-" * 50)
    
    total_size = 0
    files_count = 0
    
    for filename in os.listdir(log_dir):
        if filename.endswith('.log'):
            filepath = os.path.join(log_dir, filename)
            size = os.path.getsize(filepath)
            mod_time = os.path.getmtime(filepath)
            mod_date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M')
            
            print(f"📄 {filename}")
            print(f"   Размер: {size:,} байт ({size/1024:.1f} КБ)")
            print(f"   Изменён: {mod_date}")
            print()
            
            total_size += size
            files_count += 1
    
    print(f"📈 Итого: {files_count} файлов, {total_size:,} байт ({total_size/1024/1024:.2f} МБ)")

def show_recent_errors(hours=24):
    """Показывает недавние ошибки из всех логов"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        print("❌ Папка логов не найдена")
        return
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    cutoff_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"🔍 Ошибки за последние {hours} часов (с {cutoff_str}):")
    print("-" * 60)
    
    error_count = 0
    
    for filename in os.listdir(log_dir):
        if filename.endswith('.log'):
            filepath = os.path.join(log_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if 'ERROR' in line:
                            # Извлекаем дату из строки лога
                            try:
                                date_str = line[:19]  # YYYY-MM-DD HH:MM:SS
                                log_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                                
                                if log_time >= cutoff_time:
                                    print(f"❌ {filename}:{line_num}")
                                    print(f"   {line.strip()}")
                                    print()
                                    error_count += 1
                            except ValueError:
                                continue
            except Exception as e:
                print(f"⚠️ Ошибка чтения {filename}: {e}")
    
    if error_count == 0:
        print("✅ Ошибок не найдено!")
    else:
        print(f"🔥 Найдено ошибок: {error_count}")

def show_activity_summary(hours=24):
    """Показывает сводку активности за период"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        print("❌ Папка логов не найдена")
        return
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    print(f"📊 Активность за последние {hours} часов:")
    print("-" * 50)
    
    stats = {
        'INFO': 0,
        'ERROR': 0,
        'WARNING': 0,
        'DEBUG': 0,
        'file_operations': 0,
        'database_operations': 0,
        'user_navigation': 0
    }
    
    for filename in os.listdir(log_dir):
        if filename.endswith('.log'):
            filepath = os.path.join(log_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            date_str = line[:19]
                            log_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                            
                            if log_time >= cutoff_time:
                                # Подсчитываем уровни логов
                                for level in ['INFO', 'ERROR', 'WARNING', 'DEBUG']:
                                    if f' - {level} - ' in line:
                                        stats[level] += 1
                                        break
                                
                                # Подсчитываем типы операций
                                if 'FileOperations' in line:
                                    stats['file_operations'] += 1
                                elif 'Database' in line:
                                    stats['database_operations'] += 1
                                elif any(x in line for x in ['Главная страница', 'Переход на страницу', 'выбрал канал']):
                                    stats['user_navigation'] += 1
                                    
                        except ValueError:
                            continue
            except Exception as e:
                print(f"⚠️ Ошибка чтения {filename}: {e}")
    
    print("🎯 По уровням логирования:")
    for level in ['INFO', 'ERROR', 'WARNING', 'DEBUG']:
        print(f"   {level}: {stats[level]}")
    
    print("\n🏃 По типам операций:")
    print(f"   Файловые операции: {stats['file_operations']}")
    print(f"   Операции с БД: {stats['database_operations']}")
    print(f"   Навигация пользователей: {stats['user_navigation']}")

def simulate_log_rotation():
    """Демонстрирует, как будет выглядеть ротация логов"""
    print("🔄 Симуляция ротации логов:")
    print("-" * 40)
    
    current_date = datetime.now()
    
    print("📅 Основной лог (ротация каждый месяц):")
    for i in range(12):
        month_date = current_date - timedelta(days=30*i)
        filename = f"virtualstudio.log.{month_date.strftime('%Y-%m')}"
        print(f"   {filename}")
    
    print("\n📅 Логи операций (ротация каждые 2 недели):")
    for i in range(12):
        week_date = current_date - timedelta(days=14*i)
        for log_type in ['file_operations', 'database']:
            filename = f"{log_type}.log.{week_date.strftime('%Y-%m-%d')}"
            print(f"   {filename}")

def cleanup_logs():
    """Запускает очистку старых логов"""
    print("🧹 Очистка старых логов...")
    
    try:
        cleanup_old_logs()
        print("✅ Очистка завершена успешно")
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")

def monitor_log_size():
    """Мониторинг размера логов в реальном времени"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        print("❌ Папка логов не найдена")
        return
    
    print("📏 Мониторинг размера логов (нажмите Ctrl+C для выхода):")
    print("-" * 60)
    
    try:
        while True:
            total_size = 0
            files_info = []
            
            for filename in os.listdir(log_dir):
                if filename.endswith('.log'):
                    filepath = os.path.join(log_dir, filename)
                    size = os.path.getsize(filepath)
                    total_size += size
                    files_info.append((filename, size))
            
            # Очищаем экран
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print(f"📊 Мониторинг логов - {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 60)
            
            for filename, size in sorted(files_info):
                size_kb = size / 1024
                size_mb = size / 1024 / 1024
                
                if size_mb > 1:
                    print(f"📄 {filename:25} {size_mb:6.2f} МБ")
                else:
                    print(f"📄 {filename:25} {size_kb:6.1f} КБ")
            
            print("-" * 60)
            print(f"📈 Общий размер: {total_size/1024/1024:.2f} МБ")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n✅ Мониторинг остановлен")

def main():
    """Главное меню утилиты управления логами"""
    while True:
        print("\n" + "="*50)
        print("🛠️  УПРАВЛЕНИЕ ЛОГАМИ VIRTUALSTUDIO")
        print("="*50)
        print("1. 📊 Показать статистику логов")
        print("2. 🔍 Показать недавние ошибки")
        print("3. 📈 Сводка активности")
        print("4. 🔄 Симуляция ротации логов")
        print("5. 🧹 Очистить старые логи")
        print("6. 📏 Мониторинг размера (реальное время)")
        print("0. 🚪 Выход")
        print("-" * 50)
        
        choice = input("Выберите опцию: ").strip()
        
        if choice == '1':
            show_log_stats()
        elif choice == '2':
            hours = input("Количество часов (по умолчанию 24): ").strip()
            hours = int(hours) if hours.isdigit() else 24
            show_recent_errors(hours)
        elif choice == '3':
            hours = input("Количество часов (по умолчанию 24): ").strip()
            hours = int(hours) if hours.isdigit() else 24
            show_activity_summary(hours)
        elif choice == '4':
            simulate_log_rotation()
        elif choice == '5':
            cleanup_logs()
        elif choice == '6':
            monitor_log_size()
        elif choice == '0':
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор, попробуйте снова")
        
        input("\nНажмите Enter для продолжения...")

if __name__ == "__main__":
    main() 