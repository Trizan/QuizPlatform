document.addEventListener('DOMContentLoaded', function() {

    // Function to show temporary notifications
    function showNotification(message) {
        const notifArea = document.getElementById('notification-area');
        const notif = document.createElement('div');
        notif.className = "bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4";
        notif.textContent = message;
        notifArea.appendChild(notif);
        setTimeout(() => {
            notif.remove();
        }, 3000);
    }

    // Handle answer submission for a given quiz form
    function handleQuizSubmission(form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const selected = form.querySelector('input[name="answer"]:checked');
            if (!selected) {
                alert("Please select an answer.");
                return;
            }
            const card = form.closest('.quiz-card');
            const quizId = card.getAttribute('data-quiz-id');
            const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
            try {
                const response = await fetch('/submit-quiz-answer/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        quiz_id: quizId,
                        answer: parseInt(selected.value)
                    })
                });
                const data = await response.json();
                if (!response.ok) {
                    alert(data.error || "Submission error");
                    return;
                }
                // Remove the card from the pending list
                card.remove();
                // Build a new card element for the completed quiz
                const completedCard = document.createElement('div');
                completedCard.className = "bg-white shadow rounded-lg p-6 quiz-card";
                completedCard.setAttribute('data-quiz-id', quizId);
                // (For simplicity, we reuse much of the old inner HTML.
                // In production you might re-render this via a template or API.)
                completedCard.innerHTML = `
                    ${card.innerHTML}
                    <div class="quiz-result mt-4">
                        <p class="font-semibold ${data.is_correct ? 'text-green-600' : 'text-red-600'}">
                            ${data.is_correct ? '✓ Correct!' : '✗ Incorrect. The correct answer was option ' + data.correct_answer + '.'}
                        </p>
                        <button class="show-explanation-btn bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Show Explanation</button>
                        <div class="quiz-explanation hidden mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                            <h4 class="font-bold mb-2">Explanation:</h4>
                            <p>${data.explanation}</p>
                        </div>
                    </div>
                `;
                // Append to the completed quizzes section
                document.getElementById('completed-quizzes').appendChild(completedCard);
                // Add toggle functionality for explanation
                addExplanationToggle(completedCard);
                // Show a notification to the user
                showNotification(data.is_correct ? "Correct answer!" : `Incorrect answer. Correct option: ${data.correct_answer}`);
            } catch (error) {
                alert(error.message);
            }
        });
    }

    // Attach submission handlers to all pending quiz forms
    document.querySelectorAll('#pending-quizzes .quiz-attempt-form').forEach(form => {
        handleQuizSubmission(form);
    });

    // Function to add explanation toggle functionality to a quiz card
    function addExplanationToggle(card) {
        const btn = card.querySelector('.show-explanation-btn');
        const explanationDiv = card.querySelector('.quiz-explanation');
        if (btn && explanationDiv) {
            btn.addEventListener('click', function() {
                explanationDiv.classList.toggle('hidden');
            });
        }
    }
    
    // Initialize explanation toggles for already completed quizzes
    document.querySelectorAll('#completed-quizzes .quiz-card').forEach(card => {
        addExplanationToggle(card);
    });

    // Auto-update pending feed every 10 seconds (optional)
    setInterval(async () => {
        try {
            const response = await fetch('/ajax/quiz_feed_update/', {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            if (response.ok) {
                const data = await response.json();
                document.getElementById('pending-quizzes').innerHTML = data.html;
                // Re-attach submission handlers to the new forms
                document.querySelectorAll('#pending-quizzes .quiz-attempt-form').forEach(form => {
                    handleQuizSubmission(form);
                });
            }
        } catch (error) {
            console.error("Error fetching new quizzes:", error);
        }
    }, 10000);

});
