// Глобальные переменные
let currentDrivingVideo = null;
let currentStage = 'selection'; // 'selection', 'animation', 'background_removal'
let currentResultPath = null;

// DOM элементы
const sourceImage = document.getElementById('source-image');
const drivingVideo = document.getElementById('driving-video');
const videoPlaceholder = document.getElementById('video-placeholder');
const customVideoInput = document.getElementById('custom-video-input');
const uploadCustomVideoBtn = document.getElementById('upload-custom-video-btn');
const createAnimationBtn = document.getElementById('create-animation-btn');
const exampleVideosGrid = document.getElementById('example-videos-grid');
const loadingOverlay = document.getElementById('loading-overlay');
const loadingText = document.getElementById('loading-text');
const resultModal = document.getElementById('result-modal');
const resultVideo = document.getElementById('result-video');
const continueBtn = document.getElementById('continue-btn');
const deleteResultBtn = document.getElementById('delete-result-btn');
const notification = document.getElementById('notification');

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    loadSourceImage();
    loadExampleVideos();
    setupEventListeners();
    
    // Восстанавливаем состояние из localStorage если есть
    restoreState();
});

function loadSourceImage() {
    if (window.sourceImagePath) {
        fetch('/get_temp_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ file_path: window.sourceImagePath })
        })
        .then(response => response.blob())
        .then(blob => {
            const imageUrl = URL.createObjectURL(blob);
            sourceImage.src = imageUrl;
        })
        .catch(error => {
            console.error('Ошибка загрузки изображения:', error);
        });
    }
}

function loadExampleVideos() {
    fetch('/get_example_videos')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            exampleVideosGrid.innerHTML = '';
            data.videos.forEach(video => {
                const videoCard = createVideoCard(video);
                exampleVideosGrid.appendChild(videoCard);
            });
        }
    })
    .catch(error => {
        console.error('Ошибка загрузки примеров видео:', error);
    });
}

function createVideoCard(videoInfo) {
    const card = document.createElement('div');
    card.className = 'example-video-card';
    
    const video = document.createElement('video');
    video.src = videoInfo.url;
    video.loop = true;
    video.muted = true;
    
    const title = document.createElement('div');
    title.className = 'example-video-title';
    title.textContent = videoInfo.name;
    
    card.appendChild(video);
    card.appendChild(title);
    
    // Добавляем обработчики событий
    card.addEventListener('mouseenter', () => {
        video.play();
    });
    
    card.addEventListener('mouseleave', () => {
        video.pause();
        video.currentTime = 0;
    });
    
    card.addEventListener('click', () => {
        selectDrivingVideo(videoInfo.path, videoInfo.url);
        // Сохраняем выбор
        saveState();
    });
    
    return card;
}

function selectDrivingVideo(videoPath, videoUrl) {
    currentDrivingVideo = videoPath;
    
    // Обновляем превью
    drivingVideo.src = videoUrl;
    drivingVideo.classList.add('active');
    videoPlaceholder.style.display = 'none';
    
    // Запускаем видео
    drivingVideo.play();
    
    // Активируем кнопку создания анимации
    updateCreateButtonState();
}

function setupEventListeners() {
    uploadCustomVideoBtn.addEventListener('click', () => {
        customVideoInput.click();
    });
    
    customVideoInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            uploadCustomVideo(file);
        }
    });
    
    createAnimationBtn.addEventListener('click', () => {
        if (currentDrivingVideo) {
            startAnimationProcess();
        }
    });
    
    continueBtn.addEventListener('click', () => {
        handleContinue();
    });
    
    deleteResultBtn.addEventListener('click', () => {
        handleDelete();
    });
}

function uploadCustomVideo(file) {
    const formData = new FormData();
    formData.append('video', file);
    
    showLoadingOverlay('Загрузка видео...');
    
    fetch('/upload_custom_driving_video', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingOverlay();
        if (data.success) {
            selectDrivingVideo(data.video_path, data.video_url);
            saveState();
        } else {
            showNotification('Ошибка загрузки видео: ' + data.error);
        }
    })
    .catch(error => {
        hideLoadingOverlay();
        console.error('Ошибка:', error);
        showNotification('Ошибка загрузки видео');
    });
}

function updateCreateButtonState() {
    createAnimationBtn.disabled = !currentDrivingVideo;
}

function startAnimationProcess() {
    currentStage = 'animation';
    showLoadingOverlay('Создание анимации...');
    
    fetch('/create_animation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            source_image_path: window.sourceImagePath,
            driving_video_path: currentDrivingVideo,
            video_name: window.videoName
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingOverlay();
        if (data.success) {
            currentResultPath = data.result_path;
            showResultModal(data.result_url);
        } else {
            showNotification('Ошибка создания анимации: ' + data.error);
        }
    })
    .catch(error => {
        hideLoadingOverlay();
        console.error('Ошибка:', error);
        showNotification('Ошибка создания анимации');
    });
}

function handleContinue() {
    hideResultModal();
    
    if (currentStage === 'animation') {
        // Переходим к удалению фона
        startBackgroundRemoval();
    } else if (currentStage === 'background_removal') {
        // Сохраняем финальное видео
        saveFinalVideo();
    }
}

function startBackgroundRemoval() {
    currentStage = 'background_removal';
    showLoadingOverlay('Удаление фона...');
    
    fetch('/remove_video_background', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            video_path: currentResultPath,
            video_name: window.videoName
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingOverlay();
        if (data.success) {
            currentResultPath = data.result_path;
            showResultModal(data.result_url);
        } else {
            showNotification('Ошибка удаления фона: ' + data.error);
        }
    })
    .catch(error => {
        hideLoadingOverlay();
        console.error('Ошибка:', error);
        showNotification('Ошибка удаления фона');
    });
}

function saveFinalVideo() {
    showLoadingOverlay('Сохранение видео...');
    
    fetch('/save_final_video', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            video_path: currentResultPath,
            video_name: window.videoName
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingOverlay();
        hideResultModal();
        if (data.success) {
            showNotification('Видео успешно сохранено: ' + data.final_path);
            // Очищаем состояние
            clearState();
            setTimeout(() => {
                window.location.href = '/glavnoe';
            }, 3000);
        } else {
            showNotification('Ошибка сохранения: ' + data.error);
        }
    })
    .catch(error => {
        hideLoadingOverlay();
        hideResultModal();
        console.error('Ошибка:', error);
        showNotification('Ошибка сохранения видео');
    });
}

function handleDelete() {
    hideResultModal();
    
    // Удаляем текущий результат
    if (currentResultPath) {
        fetch('/delete_temp_result', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ file_path: currentResultPath })
        });
    }
    
    // Возвращаемся к выбору
    currentStage = 'selection';
    currentResultPath = null;
    
    // Восстанавливаем состояние выбора
    restoreState();
}

function showResultModal(videoUrl) {
    resultVideo.src = videoUrl;
    resultModal.style.display = 'flex';
}

function hideResultModal() {
    resultModal.style.display = 'none';
    resultVideo.src = '';
}

function showLoadingOverlay(text) {
    loadingText.textContent = text;
    loadingOverlay.style.display = 'flex';
}

function hideLoadingOverlay() {
    loadingOverlay.style.display = 'none';
}

function showNotification(message) {
    notification.textContent = message;
    notification.style.display = 'block';
    setTimeout(() => {
        notification.style.display = 'none';
    }, 5000);
}

// Функции сохранения и восстановления состояния
function saveState() {
    const state = {
        drivingVideo: currentDrivingVideo,
        drivingVideoSrc: drivingVideo.src
    };
    localStorage.setItem('glavnoe_animate_state', JSON.stringify(state));
}

function restoreState() {
    const savedState = localStorage.getItem('glavnoe_animate_state');
    if (savedState) {
        const state = JSON.parse(savedState);
        if (state.drivingVideo && state.drivingVideoSrc) {
            selectDrivingVideo(state.drivingVideo, state.drivingVideoSrc);
        }
    }
}

function clearState() {
    localStorage.removeItem('glavnoe_animate_state');
} 