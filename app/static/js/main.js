window.onload = function() {
    const form = document.getElementById('upload-form');
    const emotionList = document.getElementById('emotion-list');
  
    form.addEventListener('submit', function(event) {
      event.preventDefault();
      const fileInput = document.querySelector('input[type="file"]');
      const file = fileInput.files[0];
      const formData = new FormData();
      formData.append('file', file);
  
      fetch('/upload', {
        method: 'POST',
        body: formData
      })
        .then(response => response.json())
        .then(data => {
          emotionList.innerHTML = '';
          if (data.error) {
            emotionList.innerHTML = `<li class="error">${data.error}</li>`;
          } else {
            data.emotions.forEach(emotion => {
              const listItem = document.createElement('li');
              listItem.textContent = emotion;
              listItem.classList.add('emotion-item');
              emotionList.appendChild(listItem);
            });
          }
        })
        .catch(error => {
          emotionList.innerHTML = `<li class="error">${error}</li>`;
        });
    });
  };
  