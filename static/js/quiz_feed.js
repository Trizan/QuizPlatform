document.addEventListener('DOMContentLoaded', function () {

    async function handleQuizSubmission(form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            const selected = form.querySelector('input[name="answer"]:checked');
            if (!selected) {
                alert("Please select an answer.");
                return;
            }

            const card = form.closest('.quiz-card');
            const quizId = card.getAttribute('data-quiz-id');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            try {
                console.log(`Submitting answer ${selected.value} for quiz ${quizId}`);

                const response = await fetch('/submit-quiz-answer/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ quiz_id: parseInt(quizId), answer: parseInt(selected.value) })
                });

                console.log('Response received:', response);

                // Check if response is not JSON (HTML error page)
                if (!response.headers.get('content-type')?.includes('application/json')) {
                    console.error("Received HTML instead of JSON:", await response.text());
                    alert("Server error: Received HTML instead of JSON. Check Django logs.");
                    return;
                }

                // Parse JSON response
                const data = await response.json();

                if (!response.ok) {
                    console.error('Error Response:', data);
                    alert(data.error || "Something went wrong.");
                    return;
                }

                alert(data.is_correct ? "✅ Correct!" : `❌ Incorrect! The correct answer was ${data.correct_answer}`);
                card.remove();
                document.getElementById('completed-quizzes').appendChild(card);

            } catch (error) {
                console.error("AJAX error:", error);
                alert("An error occurred while submitting the quiz. Check the console for details.");
            }
        });
    }

    document.querySelectorAll('#pending-quizzes .quiz-attempt-form').forEach(form => {
        handleQuizSubmission(form);
    });

});
