#!/bin/bash

# Активация виртуального окружения
source venv/bin/activate

# Проверка наличия и версии PyTorch/CUDA
echo "Проверка версии PyTorch и CUDA..."
TORCH_INSTALLED=$(python -c "import torch; print(torch.__version__)" 2>/dev/null || echo "not_installed")
CUDA_VERSION=$(python -c "import torch; print(torch.version.cuda if torch.cuda.is_available() else 'cpu')" 2>/dev/null || echo "not_installed")

if [ "$TORCH_INSTALLED" = "not_installed" ]; then
    echo "PyTorch не установлен. Устанавливаем PyTorch с CUDA 12.1..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
elif [ "$CUDA_VERSION" = "cpu" ]; then
    echo "PyTorch установлен (${TORCH_INSTALLED}), но без поддержки CUDA. Переустанавливаем с CUDA 12.1..."
    pip uninstall -y torch torchvision torchaudio
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
elif [[ "$CUDA_VERSION" != "12.1"* ]]; then
    echo "PyTorch установлен с CUDA ${CUDA_VERSION}. Переустанавливаем с CUDA 12.1..."
    pip uninstall -y torch torchvision torchaudio
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
else
    echo "PyTorch уже установлен с CUDA 12.1 (${TORCH_INSTALLED})."
fi

# Проверка успешности установки
CUDA_VERSION_AFTER=$(python -c "import torch; print(torch.version.cuda if torch.cuda.is_available() else 'cpu')" 2>/dev/null || echo "error")
if [[ "$CUDA_VERSION_AFTER" == "12.1"* ]]; then
    echo "PyTorch с CUDA 12.1 успешно установлен."
else
    echo "Внимание: PyTorch установлен, но CUDA версии 12.1 не обнаружена (${CUDA_VERSION_AFTER})."
    echo "Проверьте наличие совместимого GPU и драйверов NVIDIA."
fi 