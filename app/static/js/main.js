const menuButton = document.querySelector("[data-menu-button]");
const mobileMenu = document.querySelector("[data-mobile-menu]");

if (menuButton && mobileMenu) {
    menuButton.addEventListener("click", () => {
        mobileMenu.classList.toggle("hidden");
    });
}

const slides = [...document.querySelectorAll(".carousel-slide")];
let activeSlide = 0;

if (slides.length > 1) {
    setInterval(() => {
        slides[activeSlide].classList.remove("is-active");
        activeSlide = (activeSlide + 1) % slides.length;
        slides[activeSlide].classList.add("is-active");
    }, 4500);
}

setTimeout(() => {
    document.querySelectorAll(".toast").forEach((toast) => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(-8px)";
        setTimeout(() => toast.remove(), 300);
    });
}, 3500);
