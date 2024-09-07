function openModal(objectNumber) {
    document.getElementById("myModal").style.display = "block";
    fetch('/get_people')
        .then(response => response.json())
        .then(data => {
            const personList = document.getElementById('personList');
            personList.innerHTML = '';
            data.forEach(person => {
                const li = document.createElement('li');
                li.innerHTML = `<strong>${person.fio}</strong> - ${person.position}`;
                li.onclick = () => selectPerson(person, objectNumber);
                personList.appendChild(li);
            });
            
            // Добавляем функциональность поиска
            const searchInput = document.getElementById('searchInput');
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                Array.from(personList.children).forEach(li => {
                    const text = li.textContent.toLowerCase();
                    li.style.display = text.includes(searchTerm) ? '' : 'none';
                });
            });
        });
}

function closeModal() {
    document.getElementById('myModal').style.display = "none";
}

function selectPerson(person, objectNumber) {
    document.getElementById(`fio${objectNumber}`).value = person.fio;
    document.getElementById(`position${objectNumber}`).value = person.position;
    document.getElementById(`photo_path${objectNumber}`).value = person.photo_path;
    document.getElementById(`proxy_path${objectNumber}`).value = person.proxy_path;
    closeModal();
}