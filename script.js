// ১. প্রোডাক্টের ডামি ডাটা (Dummy Data)
const products = [
    {
        id: 1,
        name: "স্মার্ট ওয়াচ Pro",
        category: "Fashion",
        price: 1500,
        oldPrice: 2000,
        image: "https://picsum.photos/200?random=1",
        rating: 4
    },
    {
        id: 2,
        name: "ওয়ারলেস হেডফোন",
        category: "Electronics",
        price: 2200,
        oldPrice: 2800,
        image: "https://picsum.photos/200?random=2",
        rating: 5
    },
    {
        id: 3,
        name: "স্পোর্টস রানিং জুতো",
        category: "Shoes",
        price: 1800,
        oldPrice: 2400,
        image: "https://picsum.photos/200?random=3",
        rating: 4
    },
    {
        id: 4,
        name: "ক্লাসিক লেদার ঘড়ি",
        category: "Clock",
        price: 3500,
        oldPrice: 4200,
        image: "https://picsum.photos/200?random=4",
        rating: 5
    }
];

// শপিং কার্ট অ্যারে
let cart = [];

// DOM এলিমেন্টসমূহ
const productContainer = document.getElementById('productContainer');
const cartBtn = document.getElementById('cartBtn');
const closeCart = document.getElementById('closeCart');
const cartDrawer = document.getElementById('cartDrawer');
const cartItems = document.getElementById('cartItems');
const cartCount = document.getElementById('cartCount');
const totalPrice = document.getElementById('totalPrice');

// ২. প্রোডাক্টসমূহ স্ক্রিনে ডাইনামিকালি রেন্ডার করা
function renderProducts() {
    if (!productContainer) return;
    
    productContainer.innerHTML = products.map(product => `
        <div class="product-card">
            <div class="product-img">
                <img src="${product.image}" alt="${product.name}">
            </div>
            <div class="product-info">
                <span class="category-tag">${product.category}</span>
                <h3 class="product-title">${product.name}</h3>
                <div class="rating">
                    ${'<i class="fa-solid fa-star"></i>'.repeat(product.rating)}
                    ${'<i class="fa-regular fa-star"></i>'.repeat(5 - product.rating)}
                </div>
                <div class="price-box">
                    <span class="price">৳ ${product.price.toLocaleString('bn-BD')}</span>
                    <span class="old-price">৳ ${product.oldPrice.toLocaleString('bn-BD')}</span>
                </div>
                <button class="add-to-cart-btn" onclick="addToCart(${product.id})">
                    <i class="fa-solid fa-cart-plus"></i> কার্টে যোগ করুন
                </button>
            </div>
        </div>
    `).join('');
}

// ৩. কার্টে প্রোডাক্ট যুক্ত করা
function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    const existingItem = cart.find(item => item.id === productId);

    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({ ...product, quantity: 1 });
    }

    updateCartUI();
    openCartDrawer();
}

// ৪. কার্ট UI ও টোটাল প্রাইজ আপডেট করা
function updateCartUI() {
    // কার্ট আইকন কাউন্ট আপডেট
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    cartCount.innerText = totalItems;

    // কার্ট আইটেম লিস্ট আপডেট
    if (cart.length === 0) {
        cartItems.innerHTML = '<p>আপনার কার্ট এখন খালি।</p>';
    } else {
        cartItems.innerHTML = cart.map(item => `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                <div>
                    <h4 style="font-size: 14px;">${item.name}</h4>
                    <p style="font-size: 12px; color: #666;">৳ ${item.price} x ${item.quantity}</p>
                </div>
                <button onclick="removeFromCart(${item.id})" style="background: none; border: none; color: #ff4757; cursor: pointer;">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>
        `).join('');
    }

    // মোট মূল্য গণনা
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    totalPrice.innerText = `৳ ${total.toLocaleString('bn-BD')}`;
}

// ৫. কার্ট থেকে আইটেম মুছে ফেলা
function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    updateCartUI();
}

// ৬. কার্ট ড্রয়ার অপেন ও ক্লোজ করা
function openCartDrawer() {
    cartDrawer.classList.add('active');
}

function closeCartDrawer() {
    cartDrawer.classList.remove('active');
}

// ইভেন্ট লিসেনার
if (cartBtn) cartBtn.addEventListener('click', (e) => {
    e.preventDefault();
    openCartDrawer();
});

if (closeCart) closeCart.addEventListener('click', closeCartDrawer);

// প্রাথমিক পেজ লোড রেন্ডার
document.addEventListener('DOMContentLoaded', renderProducts);
