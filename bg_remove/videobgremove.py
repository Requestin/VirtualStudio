import os
import subprocess
import argparse
from PIL import Image
from tqdm import tqdm
import shutil

# Импортируем функцию process из app.py
from app import process

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
                        fps = float(part.strip().split(' ')[0])
                        break
                if fps:
                    break
    
    if not fps:
        fps = 25  # Значение по умолчанию, если не удалось определить
    
    print(f"Извлечение кадров из видео с частотой {fps} fps...")
    
    # Извлекаем кадры с помощью ffmpeg
    output_pattern = os.path.join(output_folder, 'frame_%06d.png')
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f'fps={fps}',
        '-q:v', '1',  # Максимальное качество
        output_pattern
    ]
    
    subprocess.run(cmd, check=True)
    
    # Получаем список путей к кадрам
    frame_paths = sorted([
        os.path.join(output_folder, f) for f in os.listdir(output_folder)
        if f.startswith('frame_') and f.endswith('.png')
    ])
    
    return frame_paths, fps

def process_frames(frame_paths, output_folder, prefix="transparent_"):
    """Обрабатывает каждый кадр, удаляя фон и сохраняя с альфа-каналом"""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    processed_paths = []
    print("Удаление фона на каждом кадре и сохранение PNG с альфа-каналом...")
    
    for i, frame_path in enumerate(tqdm(frame_paths)):
        # Загружаем изображение
        img = Image.open(frame_path).convert("RGB")
        
        # Обрабатываем изображение (удаляем фон)
        transparent_img = process(img)
        
        # Сохраняем обработанное изображение с альфа-каналом
        filename = f"{prefix}{i:06d}.png"
        output_path = os.path.join(output_folder, filename)
        transparent_img.save(output_path, format="PNG")
        processed_paths.append(output_path)
    
    return processed_paths

def create_quicktime_with_alpha(input_folder, output_file, fps=30, prefix="transparent_", quality=None):
    """
    Создает QuickTime видео с альфа-каналом из последовательности PNG-изображений.
    
    Параметры:
    - input_folder: папка с PNG-изображениями
    - output_file: путь к выходному MOV-файлу
    - fps: частота кадров (кадров в секунду)
    - prefix: префикс имен файлов PNG-последовательности
    - quality: качество сжатия (1-100, где 1 - максимальное сжатие, 100 - максимальное качество)
    """
    # Проверяем наличие ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("Ошибка: ffmpeg не найден. Пожалуйста, установите ffmpeg.")
        return False
    
    # Проверяем существование входной папки
    if not os.path.exists(input_folder):
        print(f"Ошибка: папка {input_folder} не существует.")
        return False
    
    # Проверяем наличие PNG-файлов с указанным префиксом
    png_files = [f for f in os.listdir(input_folder) if f.startswith(prefix) and f.endswith('.png')]
    if not png_files:
        print(f"Ошибка: в папке {input_folder} не найдены PNG-файлы с префиксом '{prefix}'.")
        return False
    
    # Сортируем файлы по имени
    png_files.sort()
    
    print(f"Найдено {len(png_files)} PNG-файлов в папке {input_folder}")
    
    # Определяем шаблон имени файла для ffmpeg
    input_pattern = os.path.join(input_folder, f'{prefix}%06d.png')
    
    # Формируем команду ffmpeg
    cmd = [
        'ffmpeg',
        '-framerate', str(fps),
        '-i', input_pattern,
        '-c:v', 'qtrle',  # Кодек Animation для QuickTime
        '-vendor', 'ap10',  # Идентификатор производителя Apple
        '-pix_fmt', 'argb',  # Формат пикселей ARGB для поддержки альфа-канала
    ]
    
    # Добавляем параметр качества, если указан
    if quality is not None:
        # Преобразуем качество в параметр -q:v для ffmpeg (от 1 до 31, где 1 - лучшее качество)
        # Инвертируем шкалу качества от пользовательской (1-100) к ffmpeg (31-1)
        ffmpeg_quality = max(1, min(31, int(31 - (quality / 100.0 * 30))))
        cmd.extend(['-q:v', str(ffmpeg_quality)])
    
    # Добавляем выходной файл
    cmd.append(output_file)
    
    print("Создание QuickTime видео с альфа-каналом...")
    print(f"Команда: {' '.join(cmd)}")
    
    # Запускаем ffmpeg
    try:
        subprocess.run(cmd, check=True)
        print(f"Видео успешно создано: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при создании видео: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Удаление фона из видео и создание видео с альфа-каналом")
    parser.add_argument("input_video", help="Путь к входному видео")
    parser.add_argument("--output", help="Путь к выходному MOV-файлу (по умолчанию - имя_входного_файла.mov)")
    parser.add_argument("--frames-dir", help="Папка для сохранения обработанных кадров (по умолчанию - имя_входного_файла)")
    parser.add_argument("--fps", type=float, help="Частота кадров (если не указана, берется из исходного видео)")
    parser.add_argument("--prefix", help="Префикс для имен файлов", default="transparent_")
    parser.add_argument("--temp", help="Временная папка для исходных кадров (по умолчанию - temp_имя_файла)")
    parser.add_argument("--keep-temp", action="store_true", help="Сохранить временные файлы")
    parser.add_argument("--keep-frames", action="store_true", help="Сохранить обработанные кадры после создания видео")
    parser.add_argument("--quality", type=int, help="Качество сжатия (1-100, где 100 - максимальное качество)")
    args = parser.parse_args()
    
    # Определяем имя входного файла без расширения
    input_filename = os.path.basename(args.input_video)
    input_name_without_ext = os.path.splitext(input_filename)[0]  # Имя файла без расширения
    
    # Определяем имя выходного файла, если не указано явно
    if args.output is None:
        args.output = f"{input_name_without_ext}.mov"
    
    # Проверяем расширение выходного файла
    if not args.output.lower().endswith('.mov'):
        args.output += '.mov'
    
    # Определяем папку для обработанных кадров
    if args.frames_dir is None:
        args.frames_dir = input_name_without_ext
    
    # Определяем имя временной папки на основе имени входного файла, если не указано явно
    if args.temp is None:
        args.temp = f"temp_{input_name_without_ext}"
    
    # Проверяем наличие ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("Ошибка: ffmpeg не найден. Пожалуйста, установите ffmpeg.")
        return
    
    # Создаем временную папку для исходных кадров
    temp_frames_folder = args.temp
    if not os.path.exists(temp_frames_folder):
        os.makedirs(temp_frames_folder)
    
    try:
        # Шаг 1: Извлекаем кадры
        print("Шаг 1: Извлечение кадров из видео")
        frame_paths, fps = extract_frames_ffmpeg(args.input_video, temp_frames_folder, args.fps)
        
        # Шаг 2: Обрабатываем кадры (удаляем фон)
        print("\nШаг 2: Удаление фона на каждом кадре")
        processed_paths = process_frames(frame_paths, args.frames_dir, args.prefix)
        
        # Шаг 3: Создаем видео с альфа-каналом
        print("\nШаг 3: Создание видео с альфа-каналом")
        create_quicktime_with_alpha(
            args.frames_dir, 
            args.output, 
            fps=fps, 
            prefix=args.prefix,
            quality=args.quality
        )
        
        print("\nОбработка завершена!")
        print(f"Исходное видео: {args.input_video}")
        print(f"Видео с прозрачным фоном: {args.output}")
        print(f"Частота кадров: {fps} fps")
        
        # Удаляем временные файлы, если не указан флаг --keep-temp
        if not args.keep_temp:
            shutil.rmtree(temp_frames_folder)
            print(f"Временная папка {temp_frames_folder} удалена")
        else:
            print(f"Временные файлы сохранены в папке {temp_frames_folder}")
        
        # Удаляем обработанные кадры, если не указан флаг --keep-frames
        if not args.keep_frames:
            shutil.rmtree(args.frames_dir)
            print(f"Папка с обработанными кадрами {args.frames_dir} удалена")
        else:
            print(f"Обработанные кадры сохранены в папке {args.frames_dir}")
    
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        raise

if __name__ == "__main__":
    main() 