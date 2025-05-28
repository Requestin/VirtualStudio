"""
Модуль для удаления фона с видео
Основан на bg_remove/videobgremove.py, но переделан как модуль для простого импорта
"""

import os
import subprocess
import tempfile
import shutil
from PIL import Image
from tqdm import tqdm
import importlib.util

def get_process_function():
    """Получает функцию process из bg_remove/app.py"""
    try:
        bg_removal_path = os.path.join(os.path.dirname(__file__), 'bg_remove', 'app.py')
        spec = importlib.util.spec_from_file_location("bg_remove_app", bg_removal_path)
        bg_removal_app = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bg_removal_app)
        return bg_removal_app.process
    except Exception as e:
        print(f"Ошибка загрузки функции process: {e}")
        return None

def extract_frames_ffmpeg(video_path, output_folder, fps=None):
    """Извлекает кадры из видео с помощью ffmpeg"""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Получаем информацию о видео
    cmd = ['ffmpeg', '-i', video_path]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    
    # Извлекаем FPS из вывода ffmpeg, если не указан
    if fps is None:
        for line in result.stderr.split('\n'):
            if 'fps' in line and 'Stream' in line:
                parts = line.split(',')
                for part in parts:
                    if 'fps' in part:
                        try:
                            fps = float(part.strip().split()[0])
                            break
                        except:
                            continue
                if fps:
                    break
        
        if fps is None:
            fps = 30.0  # Значение по умолчанию
    
    # Извлекаем кадры
    if fps:
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vf', f'fps={fps}',
            '-q:v', '2',
            os.path.join(output_folder, 'frame_%06d.png'),
            '-y'
        ]
    else:
        cmd = [
            'ffmpeg', '-i', video_path,
            '-q:v', '2',
            os.path.join(output_folder, 'frame_%06d.png'),
            '-y'
        ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Ошибка ffmpeg: {result.stderr}")
    
    # Получаем список созданных файлов
    frame_files = []
    for filename in os.listdir(output_folder):
        if filename.startswith('frame_') and filename.endswith('.png'):
            frame_files.append(os.path.join(output_folder, filename))
    
    frame_files.sort()
    
    print(f"Извлечено {len(frame_files)} кадров с частотой {fps} fps")
    return frame_files, fps

def process_frames(frame_paths, output_folder, prefix="processed_"):
    """Обрабатывает кадры, удаляя фон"""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    process_func = get_process_function()
    if not process_func:
        raise Exception("Не удалось загрузить функцию удаления фона")
    
    processed_paths = []
    
    print(f"Обработка {len(frame_paths)} кадров...")
    for i, frame_path in enumerate(tqdm(frame_paths, desc="Удаление фона")):
        try:
            # Обрабатываем кадр
            result = process_func(frame_path)
            
            if result and len(result) > 0:
                # Результат - это PIL Image
                processed_image = result[0]
                
                # Сохраняем обработанный кадр
                frame_number = os.path.splitext(os.path.basename(frame_path))[0].split('_')[-1]
                output_filename = f"{prefix}{frame_number}.png"
                output_path = os.path.join(output_folder, output_filename)
                
                # Сохраняем как PNG с альфа-каналом
                processed_image.save(output_path, "PNG")
                processed_paths.append(output_path)
            else:
                print(f"Ошибка обработки кадра {frame_path}")
                
        except Exception as e:
            print(f"Ошибка при обработке кадра {frame_path}: {e}")
    
    print(f"Успешно обработано {len(processed_paths)} кадров")
    return processed_paths

def create_quicktime_with_alpha(frames_folder, output_path, fps=30, prefix="processed_", quality=90):
    """Создает видео QuickTime с альфа-каналом"""
    try:
        # Получаем список обработанных кадров
        frame_files = []
        for filename in os.listdir(frames_folder):
            if filename.startswith(prefix) and filename.endswith('.png'):
                frame_files.append(os.path.join(frames_folder, filename))
        
        frame_files.sort()
        
        if not frame_files:
            print("Не найдено обработанных кадров")
            return False
        
        # Создаем временную папку для пронумерованных кадров
        temp_numbered_folder = tempfile.mkdtemp(prefix="numbered_frames_")
        
        try:
            # Копируем и переименовываем кадры для ffmpeg
            for i, frame_file in enumerate(frame_files):
                new_name = f"frame_{i+1:06d}.png"
                new_path = os.path.join(temp_numbered_folder, new_name)
                shutil.copy2(frame_file, new_path)
            
            # Создаем видео с альфа-каналом используя ffmpeg
            input_pattern = os.path.join(temp_numbered_folder, "frame_%06d.png")
            
            cmd = [
                'ffmpeg',
                '-framerate', str(fps),
                '-i', input_pattern,
                '-c:v', 'prores_ks',
                '-profile:v', '4444',
                '-pix_fmt', 'yuva444p10le',
                '-q:v', str(quality),
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Видео успешно создано: {output_path}")
                return True
            else:
                print(f"Ошибка создания видео: {result.stderr}")
                return False
                
        finally:
            # Очищаем временную папку
            shutil.rmtree(temp_numbered_folder)
            
    except Exception as e:
        print(f"Ошибка при создании видео: {e}")
        return False

def remove_video_background(input_video_path, output_video_path=None, video_name="processed", fps=None):
    """
    Основная функция для удаления фона с видео
    
    Args:
        input_video_path (str): Путь к входному видео
        output_video_path (str, optional): Путь к выходному видео. Если None, создается автоматически
        video_name (str): Название для временных файлов
        fps (float, optional): Частота кадров. Если None, извлекается из видео
        
    Returns:
        str or None: Путь к выходному файлу если успешно, None если ошибка
    """
    
    if not os.path.exists(input_video_path):
        print(f"Входной файл не найден: {input_video_path}")
        return None
    
    # Создаем путь для выходного файла, если не указан
    if output_video_path is None:
        input_dir = os.path.dirname(input_video_path)
        input_name = os.path.splitext(os.path.basename(input_video_path))[0]
        output_video_path = os.path.join(input_dir, f"{input_name}_transparent.mov")
    
    # Создаем выходную папку, если не существует
    output_dir = os.path.dirname(output_video_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Создаем временные папки
    temp_base = tempfile.mkdtemp(prefix=f"video_bg_removal_{video_name}_")
    temp_frames_folder = os.path.join(temp_base, "temp_frames")
    processed_frames_folder = os.path.join(temp_base, "processed_frames")
    
    try:
        print(f"Начинаем обработку видео: {input_video_path}")
        print(f"Временная папка: {temp_base}")
        
        # Шаг 1: Извлекаем кадры
        print("Шаг 1: Извлечение кадров из видео")
        frame_paths, detected_fps = extract_frames_ffmpeg(input_video_path, temp_frames_folder, fps)
        
        if not frame_paths:
            print("Не удалось извлечь кадры из видео")
            return None
        
        # Шаг 2: Обрабатываем кадры (удаляем фон)
        print("Шаг 2: Удаление фона на каждом кадре")
        processed_paths = process_frames(frame_paths, processed_frames_folder, "transparent_")
        
        if not processed_paths:
            print("Не удалось обработать кадры")
            return None
        
        # Шаг 3: Создаем видео с альфа-каналом
        print("Шаг 3: Создание видео с альфа-каналом")
        success = create_quicktime_with_alpha(
            processed_frames_folder, 
            output_video_path, 
            fps=detected_fps, 
            prefix="transparent_",
            quality=90
        )
        
        if success and os.path.exists(output_video_path):
            print(f"Видео успешно создано: {output_video_path}")
            return output_video_path
        else:
            print("Ошибка при создании видео")
            return None
            
    except Exception as e:
        print(f"Ошибка при обработке видео: {e}")
        return None
        
    finally:
        # Очищаем временные файлы
        try:
            shutil.rmtree(temp_base)
            print(f"Временные файлы удалены: {temp_base}")
        except Exception as e:
            print(f"Ошибка при удалении временных файлов: {e}")

def quick_remove_background(input_video_path, video_name="processed"):
    """
    Быстрая функция для удаления фона - создает выходной файл автоматически
    
    Args:
        input_video_path (str): Путь к входному видео
        video_name (str): Название видео
        
    Returns:
        str or None: Путь к выходному файлу если успешно, None если ошибка
    """
    return remove_video_background(input_video_path, video_name=video_name)

if __name__ == "__main__":
    # Для тестирования
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python video_background_remover.py <input_video> [output_video]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = remove_video_background(input_path, output_path)
    if result:
        print(f"Обработка завершена успешно! Результат: {result}")
    else:
        print("Обработка завершена с ошибкой!")
        sys.exit(1) 