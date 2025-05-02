# Активация виртуального окружения
.\venv\Scripts\Activate.ps1

# Проверка наличия и версии PyTorch/CUDA
Write-Host "Проверка версии PyTorch и CUDA..."
try {
    $torchInstalled = python -c "import torch; print(torch.__version__)" 2>$null
    if (-not $?) { throw "PyTorch не установлен" }
    
    $cudaVersion = python -c "import torch; print(torch.version.cuda if torch.cuda.is_available() else 'cpu')" 2>$null
    if (-not $?) { throw "Ошибка определения версии CUDA" }
    
    if ($cudaVersion -eq "cpu") {
        Write-Host "PyTorch установлен ($torchInstalled), но без поддержки CUDA. Переустанавливаем с CUDA 12.1..."
        pip uninstall -y torch torchvision torchaudio
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    }
    elseif (-not $cudaVersion.StartsWith("12.1")) {
        Write-Host "PyTorch установлен с CUDA $cudaVersion. Переустанавливаем с CUDA 12.1..."
        pip uninstall -y torch torchvision torchaudio
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    }
    else {
        Write-Host "PyTorch уже установлен с CUDA 12.1 ($torchInstalled)."
    }
}
catch {
    Write-Host "PyTorch не установлен или произошла ошибка. Устанавливаем PyTorch с CUDA 12.1..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
}

# Проверка успешности установки
try {
    $cudaVersionAfter = python -c "import torch; print(torch.version.cuda if torch.cuda.is_available() else 'cpu')" 2>$null
    if ($cudaVersionAfter.StartsWith("12.1")) {
        Write-Host "PyTorch с CUDA 12.1 успешно установлен."
    }
    else {
        Write-Host "Внимание: PyTorch установлен, но CUDA версии 12.1 не обнаружена ($cudaVersionAfter)."
        Write-Host "Проверьте наличие совместимого GPU и драйверов NVIDIA."
    }
}
catch {
    Write-Host "Ошибка при проверке установки PyTorch."
} 