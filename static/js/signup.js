// hamburger.js

document.addEventListener('DOMContentLoaded', () => {
    // Select the hamburger menu and nav links
    const hamburger = document.querySelector('.hamburger-menu');
    const navLinks = document.querySelector('.nav-links');

    // Add click event listener to the hamburger menu
    hamburger.addEventListener('click', () => {
        // Toggle the active class on nav links
        navLinks.classList.toggle('active');
    });

    // Close the menu when a link is clicked (optional)
    const links = navLinks.querySelectorAll('a');
    links.forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
        });
    });
});