document.addEventListener("DOMContentLoaded", () => {
    updateCartCount();
});

function addToCart(productId) {
    let cart = JSON.parse(localStorage.getItem("cart") || "{}");
    cart[productId] = (cart[productId] || 0) + 1;
    localStorage.setItem("cart", JSON.stringify(cart));
    updateCartCount();
}

function updateCartCount() {
    let cart = JSON.parse(localStorage.getItem("cart") || "{}");
    let total = Object.values(cart).reduce((a, b) => a + b, 0);
    let countElement = document.getElementById("cart-count");
    if (countElement) countElement.textContent = total;
}
