document.addEventListener("DOMContentLoaded", function () {
    const hamburgerMenu = document.querySelector(".hamburger-menu");
    const navLinks = document.querySelector(".nav-links");

    hamburgerMenu.addEventListener("click", function () {
        navLinks.classList.toggle("active");
        hamburgerMenu.classList.toggle("open");
    });

    navLinks.addEventListener("click", function (event) {
        if (event.target.tagName === "A") {
            navLinks.classList.remove("active");
            hamburgerMenu.classList.remove("open");
        }
    });
});