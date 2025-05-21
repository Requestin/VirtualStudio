const previewContainer = document.getElementById('preview-container');
        const previewImage = document.getElementById('preview-image');
        const fileInput = document.getElementById('file-input');
        const uploadBtn = document.getElementById('upload-btn');
        const saveBtn = document.getElementById('save-btn');
        const nameInput = document.getElementById('name-input');
        const positionInput = document.getElementById('position-input');
        const resultModal = document.getElementById('result-modal');
        const resultImageContainer = document.getElementById('result-image-container');
        const resultImage = document.getElementById('result-image');
        const commentContainer = document.getElementById('comment-container');
        const continueBtnContainer = document.getElementById('continue-btn-container');
        const deleteBtnContainer = document.getElementById('delete-btn-container');
        const continueBtn = document.getElementById('continue-btn');
        const deleteBtn = document.getElementById('delete-btn');
        const deleteComment = document.getElementById('delete-comment');
        const notification = document.getElementById('notification');

        let isDragging = false;
        let startX, startY;
        let scale = 1;
        let currentImageFile = null;
        let currentImageName = '';
        let isImageLoaded = false;
        let isSaving = false;
        let savedFilePath = '';

        uploadBtn.addEventListener('click', function() {
            console.log('Кнопка загрузки нажата');
            fileInput.click();
        });

        function checkFormValidity() {
            const isNameFilled = nameInput.value.trim() !== '';
            const isPositionFilled = positionInput.value.trim() !== '';

            if (isImageLoaded && isNameFilled && isPositionFilled) {
                saveBtn.disabled = false;
            } else {
                saveBtn.disabled = true;
            }
        }

        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                currentImageName = file.name;
                loadImage(file);
            }
        });

        nameInput.addEventListener('input', checkFormValidity);
        positionInput.addEventListener('input', checkFormValidity);

        function loadImage(file) {
            currentImageFile = file;
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImage.src = e.target.result;
                previewImage.onload = () => {
                    centerAndScaleImage();
                    isImageLoaded = true;
                    checkFormValidity();
                };
            };
            reader.readAsDataURL(file);
        }

        function centerAndScaleImage() {
            const containerWidth = previewContainer.offsetWidth;
            const containerHeight = previewContainer.offsetHeight;
            const imageWidth = previewImage.naturalWidth;
            const imageHeight = previewImage.naturalHeight;

            const containerAspectRatio = containerWidth / containerHeight;
            const imageAspectRatio = imageWidth / imageHeight;

            if (containerAspectRatio > imageAspectRatio) {
                scale = containerHeight / imageHeight;
            } else {
                scale = containerWidth / imageWidth;
            }

            const scaledWidth = imageWidth * scale;
            const scaledHeight = imageHeight * scale;

            const left = (containerWidth - scaledWidth) / 2;
            const top = (containerHeight - scaledHeight) / 2;

            previewImage.style.width = `${scaledWidth}px`;
            previewImage.style.height = `${scaledHeight}px`;
            previewImage.style.left = `${left}px`;
            previewImage.style.top = `${top}px`;
        }

        previewContainer.addEventListener('mousedown', startDragging);
        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', stopDragging);
        previewContainer.addEventListener('wheel', handleWheel);
        previewContainer.addEventListener('auxclick', handleMiddleClick);

        previewImage.addEventListener('dragstart', (e) => e.preventDefault());

        function startDragging(e) {
            if (e.button === 0 && isImageLoaded) {
                isDragging = true;
                startX = e.clientX - previewImage.offsetLeft;
                startY = e.clientY - previewImage.offsetTop;
                e.preventDefault();
            }
        }

        function drag(e) {
            if (isDragging && isImageLoaded) {
                e.preventDefault();
                const x = e.clientX - startX;
                const y = e.clientY - startY;
                previewImage.style.left = `${x}px`;
                previewImage.style.top = `${y}px`;
            }
        }

        function stopDragging() {
            isDragging = false;
        }

        function handleWheel(e) {
            if (isImageLoaded) {
                e.preventDefault();
                const delta = e.deltaY > 0 ? 0.95 : 1.05;
                scale *= delta;
                scale = Math.max(0.1, Math.min(scale, 5));

                const newWidth = previewImage.naturalWidth * scale;
                const newHeight = previewImage.naturalHeight * scale;

                const left = parseFloat(previewImage.style.left) + (previewImage.offsetWidth - newWidth) / 2;
                const top = parseFloat(previewImage.style.top) + (previewImage.offsetHeight - newHeight) / 2;

                previewImage.style.width = `${newWidth}px`;
                previewImage.style.height = `${newHeight}px`;
                previewImage.style.left = `${left}px`;
                previewImage.style.top = `${top}px`;
            }
        }

        function handleMiddleClick(e) {
            if (e.button === 1 && currentImageFile) {
                e.preventDefault();
                loadImage(currentImageFile);
            }
        }

        function showLoadingOverlay() {
            document.getElementById('loading-overlay').style.display = 'flex';
        }
        
        function hideLoadingOverlay() {
            document.getElementById('loading-overlay').style.display = 'none';
        }

        function showNotification(message) {
            notification.textContent = message;
            notification.style.display = 'block';
            setTimeout(() => {
                notification.style.display = 'none';
            }, 1000);
        }

        function showResultModal() {
            document.getElementById('modal-overlay').style.display = 'block';
            resultModal.style.display = 'flex';
            resultImageContainer.style.display = 'block';
            commentContainer.style.display = 'flex';
            continueBtnContainer.style.display = 'block';
            deleteBtnContainer.style.display = 'block';
        }

        function hideResultModal() {
            document.getElementById('modal-overlay').style.display = 'none';
            resultModal.style.display = 'none';
            resultImageContainer.style.display = 'none';
            commentContainer.style.display = 'none';
            continueBtnContainer.style.display = 'none';
            deleteBtnContainer.style.display = 'none';
        }

        saveBtn.addEventListener('click', (e) => {
            if (saveBtn.disabled) {
                e.preventDefault();
                alert("Проверьте правильность введенных вами данных!");
                return;
            }

            isSaving = true;
            showLoadingOverlay();
            
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = 607;
            canvas.height = 749;

            const rect = previewImage.getBoundingClientRect();
            const containerRect = previewContainer.getBoundingClientRect();

            ctx.drawImage(
                previewImage,
                (containerRect.left - rect.left) / scale,
                (containerRect.top - rect.top) / scale,
                containerRect.width / scale,
                containerRect.height / scale,
                0, 0, 607, 749
            );

            const imageData = canvas.toDataURL('image/png');

            const name = nameInput.value;
            const position = positionInput.value;

            fetch('/save_image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: imageData,
                    name: name,
                    position: position
                })
            })
            .then(response => response.json())
            .then(data => {
                hideLoadingOverlay();
                isSaving = false;
                if (data.success) {
                    savedFilePath = data.file_path;
                    const filePath = `/get_image/${encodeURIComponent(data.file_path)}`;
                    resultImage.src = filePath;
                    showResultModal(); // Отображаем модальное окно
                } else {
                    alert('Ошибка при обработке изображения: ' + data.error);
                }
            })
            .catch(error => {
                hideLoadingOverlay();
                isSaving = false;
                console.error('Ошибка:', error);
                alert('Произошла ошибка при сохранении изображения');
            });
        });

        deleteBtn.addEventListener('click', () => {
            const comment = deleteComment.value.trim();

            fetch('/delete_image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    file_path: savedFilePath,
                    comment: comment
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    hideResultModal();
                    showNotification('Фото удалено');
                    setTimeout(() => {
                        location.reload();
                    }, 2000);
                } else {
                    alert('Ошибка при перемещении изображения: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при перемещении изображения');
            });
        });
        
        checkFormValidity();
// ... (оставьте весь предыдущий код без изменений) ...

continueBtn.addEventListener('click', () => {
    if (!savedFilePath) {
        console.error('Путь к сохраненному изображению отсутствует');
        return;
    }

    showLoadingOverlay();
    const name = nameInput.value;
    const position = positionInput.value;
    fetch('/continue_processing', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ file_path: savedFilePath,
            name: name,
            position: position,
         })
    })
    .then(response => response.json())
    .then(result => {
        hideLoadingOverlay();
        if (result.success) {
            console.log('Аватар успешно создан:', result.avatar_path);
            hideResultModal();
            showNotification('Фото успешно сохранено');
            setTimeout(() => {
                location.reload();
            }, 2000);
        } else {
            console.error('Ошибка при создании аватара:', result.error);
            alert('Ошибка при создании аватара: ' + result.error);
        }
    })
    .catch(error => {
        hideLoadingOverlay();
        console.error('Ошибка:', error);
        alert('Произошла ошибка при создании аватара');
    });
});
// ... (оставьте весь последующий код без изменений) ...
