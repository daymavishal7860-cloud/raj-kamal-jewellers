const header = document.querySelector("[data-site-header]");
const menuButton = document.querySelector("[data-menu-button]");
const mobileMenu = document.querySelector("[data-mobile-menu]");
const mobilePanel = document.querySelector("[data-mobile-panel]");
const closeButtons = document.querySelectorAll("[data-menu-close]");

const syncHeader = () => {
    if (!header) return;
    header.classList.toggle("is-scrolled", window.scrollY > 24);
};

syncHeader();
window.addEventListener("scroll", syncHeader, { passive: true });

const setMenu = (open) => {
    if (!mobileMenu || !mobilePanel || !menuButton) return;
    mobileMenu.classList.toggle("is-open", open);
    mobileMenu.classList.toggle("pointer-events-none", !open);
    mobilePanel.classList.toggle("translate-x-full", !open);
    menuButton.setAttribute("aria-expanded", String(open));
    document.body.classList.toggle("overflow-hidden", open);
};

if (menuButton) {
    menuButton.addEventListener("click", () => setMenu(!mobileMenu.classList.contains("is-open")));
}

closeButtons.forEach((button) => {
    button.addEventListener("click", () => setMenu(false));
});

const slides = [...document.querySelectorAll(".carousel-slide")];
let activeSlide = 0;

if (slides.length > 1) {
    setInterval(() => {
        slides[activeSlide].classList.remove("is-active");
        activeSlide = (activeSlide + 1) % slides.length;
        slides[activeSlide].classList.add("is-active");
    }, 5200);
}

const revealItems = document.querySelectorAll("[data-reveal]");
if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("is-visible");
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.14 });
    revealItems.forEach((item) => observer.observe(item));
} else {
    revealItems.forEach((item) => item.classList.add("is-visible"));
}

setTimeout(() => {
    document.querySelectorAll(".toast").forEach((toast) => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(-8px)";
        setTimeout(() => toast.remove(), 300);
    });
}, 3500);
