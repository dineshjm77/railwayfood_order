// Initialize cart from localStorage or an empty array
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// Function to add an item to the cart
function addToCart(item) {
    // Check if item already exists in cart and update its quantity
    const existingItemIndex = cart.findIndex(cartItem => cartItem.name === item.name);
    
    if (existingItemIndex !== -1) {
        cart[existingItemIndex].quantity += item.quantity; // Increase quantity if item already exists
    } else {
        cart.push(item); // Add the item to the cart if it's not already there
    }

    // Save updated cart to localStorage
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartBadge(); // Update the cart badge to reflect the new number of items
}

// Function to update the cart badge with the total quantity of items
function updateCartBadge() {
    const badge = document.querySelector('#shopping-cart .badge');
    badge.textContent = cart.reduce((acc, item) => acc + item.quantity, 0); // Count total items in cart
}

// Add event listener to 'Add to Cart' buttons
document.querySelectorAll('.food-menu-box form').forEach((form) => {
    form.addEventListener('submit', (e) => {
        e.preventDefault();

        // Extract food details from the form
        const foodName = form.querySelector('h4').textContent.trim();
        const priceText = form.querySelector('.food-price').textContent.trim();
        const quantityInput = form.querySelector('input[type="number"]');
        const quantity = parseInt(quantityInput.value, 10);

        // Parse price from text
        const price = parseFloat(priceText.replace('₹', '').trim());

        if (isNaN(price) || isNaN(quantity) || quantity <= 0) {
            alert('Invalid price or quantity. Please enter a valid number.');
            return;
        }

        const item = {
            name: foodName,
            price: price,
            quantity: quantity
        };

        // Add item to cart
        addToCart(item);
    });
});

// Initialize cart badge on page load
updateCartBadge();
