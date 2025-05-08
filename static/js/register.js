// Script to handle form submission for registration asynchronously
document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');

    if (registerForm) {
        registerForm.addEventListener('submit', (event) => {
            event.preventDefault(); // Prevent default form submission

            const formData = new FormData(registerForm);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(registerForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken,  // Include CSRF token in headers
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Redirect to home page on successful registration
                    window.location.href = data.redirect_url;
                } else {
                    // Display error messages
                    const errorContainer = document.getElementById('errorContainer');
                    if (errorContainer) {
                        errorContainer.innerHTML = Object.values(data.errors).join('<br>');
                    }
                }
            })
            .catch(error => {
                console.error('Error during registration:', error);
            });
        });
    }
});