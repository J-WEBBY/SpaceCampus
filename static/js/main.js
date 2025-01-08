// Select elements
const hamburger = document.querySelector('.hamburger-menu');
const navLinks = document.querySelector('.nav-links');

// Toggle navigation menu on hamburger click
hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('mobile'); // Toggles mobile menu
    navLinks.classList.toggle('active'); // Toggles visibility of the menu

    // Animate hamburger lines
    hamburger.classList.toggle('active');
});

// Close the menu when a link is clicked (optional)
const navItems = document.querySelectorAll('.nav-links li a');
navItems.forEach((item) => {
    item.addEventListener('click', () => {
        navLinks.classList.remove('mobile'); // Ensures menu closes on mobile
        navLinks.classList.remove('active'); // Hides menu
        hamburger.classList.remove('active'); // Resets hamburger animation
    });
});

// Close the menu if clicking outside (optional)
document.addEventListener('click', (e) => {
    if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
        navLinks.classList.remove('mobile'); // Ensures menu closes on mobile
        navLinks.classList.remove('active'); // Hides menu
        hamburger.classList.remove('active'); // Resets hamburger animation
    }
});
