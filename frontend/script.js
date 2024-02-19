document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.getElementById('signupForm');
    const loginForm = document.getElementById('loginForm');
    const message = document.getElementById('message');

    signupForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(signupForm);

        // Convert FormData to JSON object
        const jsonData = {};
        formData.forEach((value, key) => {
            jsonData[key] = value;
        });

        fetch('http://localhost:8080/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json' // Specify JSON content type
            },
            body: JSON.stringify(jsonData) // Convert JSON object to string
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                message.textContent = 'Signup successful!';
                if (data.redirect) {
                    // Redirect to the specified URL after successful signup
                    window.location.href = data.redirect;
                }
            } else {
                message.textContent = data.message;
            }
        })        
        .catch(error => {
            console.error('Error:', error);
            message.textContent = 'Server error!';
        });
    });

    loginForm.addEventListener('submit', function(event) {
        event.preventDefault();

        console.log('Login form submitted'); // Log when the form is submitted

        const formData = new FormData(loginForm);

        // Convert FormData to JSON object
        const jsonData = {};
        formData.forEach((value, key) => {
            jsonData[key] = value;
        });

        fetch('http://localhost:8080/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json' // Specify JSON content type
            },
            body: JSON.stringify(jsonData) // Convert JSON object to string
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                message.textContent = 'Login successful!';
                if (data.redirect) {
                    // Redirect to the specified URL after successful login
                    window.location.href = data.redirect;
                }
            } else {
                message.textContent = data.message;
            }
        })        
        .catch(error => {
            console.error('Error:', error);
            message.textContent = 'Server error!';
        });
    });
});
