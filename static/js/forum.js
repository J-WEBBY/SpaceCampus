// forum.js

document.addEventListener("DOMContentLoaded", function () {
    // Select the hamburger menu and the navigation links
    const hamburgerMenu = document.querySelector(".hamburger-menu");
    const navLinks = document.querySelector(".nav-links");

    // Add a click event listener to the hamburger menu
    hamburgerMenu.addEventListener("click", function () {
        // Toggle the active class on the navigation links
        navLinks.classList.toggle("active");

        // Toggle the hamburger menu animation
        hamburgerMenu.classList.toggle("active");
    });
});