import torch
import sys

def check_torch_cuda():
    # Проверка версии PyTorch
    print(f"Версия PyTorch: {torch.__version__}")
    
    # Проверка доступности CUDA
    cuda_available = torch.cuda.is_available()
    print(f"CUDA доступен: {cuda_available}")
    
    if cuda_available:
        # Получение версии CUDA
        cuda_version = torch.version.cuda
        print(f"Версия CUDA: {cuda_version}")
        
        # Количество доступных GPU
        device_count = torch.cuda.device_count()
        print(f"Количество доступных GPU: {device_count}")
        
        # Информация о каждом GPU
        for i in range(device_count):
            device_name = torch.cuda.get_device_name(i)
            print(f"GPU {i}: {device_name}")
            
        # Текущее устройство
        current_device = torch.cuda.current_device()
        print(f"Текущее устройство: {current_device}")
        
        # Проверка работы с CUDA
        try:
            # Создаем тензор на GPU
            x = torch.tensor([1.0, 2.0, 3.0], device='cuda')
            print(f"Тестовый тензор на GPU: {x}")
            print("Тест успешно пройден: PyTorch работает с CUDA")
        except Exception as e:
            print(f"Ошибка при создании тензора на GPU: {e}")
    else:
        print("CUDA недоступен. PyTorch будет работать только на CPU.")
        print("Возможные причины:")
        print("1. Драйверы NVIDIA не установлены или устарели")
        print("2. У вас нет совместимой GPU от NVIDIA")
        print("3. Установлена версия PyTorch без поддержки CUDA")

if __name__ == "__main__":
    check_torch_cuda()