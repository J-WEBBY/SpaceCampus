// Profile.js: JavaScript for Profile Page Functionality

// Handle Profile Image Preview
document.getElementById('profile-image').addEventListener('change', function (event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            document.querySelector('.profile-image').src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});

// Form Validation for Profile Update
document.querySelector('form[action="/profile/update"]').addEventListener('submit', function (event) {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (password && password.length < 6) {
        event.preventDefault();
        alert('Password must be at least 6 characters long.');
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        event.preventDefault();
        alert('Please enter a valid email address.');
    }
});

// Fade Out Flash Messages After 3 Seconds
const flashMessages = document.querySelectorAll('.flash-message');
flashMessages.forEach(message => {
    setTimeout(() => {
        message.style.display = 'none';
    }, 3000);
});

// Confirm Account Deletion
document.querySelector('.btn-danger').addEventListener('click', function (event) {
    const confirmed = confirm('Are you sure you want to delete your account? This action is irreversible.');
    if (!confirmed) {
        event.preventDefault();
    }
});

// Hamburger Menu Functionality
document.querySelector('.hamburger-menu').addEventListener('click', function () {
    document.querySelector('.nav-links').classList.toggle('active');
});