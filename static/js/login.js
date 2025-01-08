// login.js: JavaScript for Hamburger Menu Functionality

document.addEventListener('DOMContentLoaded', () => {
    const hamburger = document.querySelector('.hamburger-menu');
    const navLinks = document.querySelector('.nav-links');

    // Toggle the active class on the nav-links when the hamburger is clicked
    hamburger.addEventListener('click', () => {
        navLinks.classList.toggle('active');
    });

    // Close the menu if a link is clicked
    navLinks.addEventListener('click', (event) => {
        if (event.target.tagName === 'A') {
            navLinks.classList.remove('active');
        }
    });
});