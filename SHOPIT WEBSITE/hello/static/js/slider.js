let index = 0;
const slides = document.getElementById("slideContainer");
const total = slides.children.length;

function updateSlide() {
    slides.style.transform = `translateX(-${index * 100}%)`;
}

function nextSlide() {
    if (index < total - 1) {
        index++;
    } else {
        index = 0; // loop
    }
    updateSlide();
}

function prevSlide() {
    if (index > 0) {
        index--;
    } else {
        index = total - 1;
    }
    updateSlide();
}
