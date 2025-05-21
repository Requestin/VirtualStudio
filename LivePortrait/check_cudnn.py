import ctypes
import os
import glob

def find_cudnn_dll():
    # Добавляем новый путь в список поиска
    possible_paths = [
        "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.1/bin",
        "C:/Program Files/NVIDIA/CUDNN/v*/bin",
        "C:/Program Files/NVIDIA/CUDNN/v*/bin/12.9",  # Добавляем новый путь
        "C:/Program Files/NVIDIA Corporation/CUDNN/v*/bin"
    ]
    
    found_files = []
    for path_pattern in possible_paths:
        for path in glob.glob(path_pattern):
            dll_files = glob.glob(os.path.join(path, "cudnn*.dll"))
            found_files.extend(dll_files)
    
    return found_files

def copy_cudnn_to_cuda(cudnn_path):
    """Копирует файлы cuDNN в директорию CUDA"""
    cuda_bin = "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.1/bin"
    if not os.path.exists(cuda_bin):
        print(f"Директория CUDA не найдена: {cuda_bin}")
        return False
        
    try:
        import shutil
        cudnn_dir = os.path.dirname(cudnn_path)
        # Копируем все DLL файлы
        for dll in glob.glob(os.path.join(cudnn_dir, "cudnn*.dll")):
            dest = os.path.join(cuda_bin, os.path.basename(dll))
            if not os.path.exists(dest):
                shutil.copy2(dll, dest)
                print(f"Скопирован файл: {dll} -> {dest}")
        return True
    except Exception as e:
        print(f"Ошибка при копировании: {str(e)}")
        return False

print("Поиск файлов cuDNN...")
cudnn_files = find_cudnn_dll()

if cudnn_files:
    print("\nНайденные файлы cuDNN:")
    for file in cudnn_files:
        print(f" - {file}")
    
    try:
        # Пробуем загрузить первый найденный файл
        ctypes.CDLL(cudnn_files[0])
        print(f"\ncuDNN успешно загружен: {cudnn_files[0]}")
        
        # Предлагаем скопировать файлы
        print("\nХотите скопировать файлы cuDNN в директорию CUDA? (y/n)")
        if input().lower() == 'y':
            if copy_cudnn_to_cuda(cudnn_files[0]):
                print("Файлы успешно скопированы")
            else:
                print("Не удалось скопировать файлы")
    except Exception as e:
        print(f"\nОшибка при загрузке cuDNN: {str(e)}")
else:
    print("Файлы cuDNN не найдены")