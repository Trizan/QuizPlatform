// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (navToggle) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }

    // Quiz form validation
    const quizForm = document.getElementById('quizForm');
    if (quizForm) {
        quizForm.addEventListener('submit', (e) => {
            const selectedOption = quizForm.querySelector('input[name="answer"]:checked');
            if (!selectedOption) {
                e.preventDefault();
                alert('Please select an answer');
            }
        });
    }

    // Notification polling
    function updateNotificationCount() {
        fetch('/notifications/count/')
            .then(response => response.json())
            .then(data => {
                const count = document.getElementById('notificationCount');
                if (count) {
                    count.textContent = data.count;
                    count.style.display = data.count > 0 ? 'inline' : 'none';
                }
            });
    }

    // Update notifications every 30 seconds
    if (document.querySelector('.notifications-link')) {
        updateNotificationCount();
        setInterval(updateNotificationCount, 30000);
    }

    // Profile picture preview
    const profilePicInput = document.getElementById('id_profile_picture');
    const previewImage = document.getElementById('profile-preview');
    
    if (profilePicInput && previewImage) {
        profilePicInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImage.src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // Topic selection validation
    const topicForm = document.querySelector('form');
    if (topicForm && topicForm.querySelector('input[name="topics"]')) {
        topicForm.addEventListener('submit', (e) => {
            const selectedTopics = topicForm.querySelectorAll('input[name="topics"]:checked');
            if (selectedTopics.length !== 5) {
                e.preventDefault();
                alert('Please select exactly 5 topics');
            }
        });
    }
});