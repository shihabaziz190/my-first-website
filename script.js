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
// ==========================================
// ৭. কন্টাক্ট ফর্ম ক্লায়েন্ট-সাইড ভ্যালিডেশন
// ==========================================
const contactForm = document.getElementById('contactForm');

if (contactForm) {
    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');
    const phoneInput = document.getElementById('phone');
    const messageInput = document.getElementById('message');
    const formStatus = document.getElementById('formStatus');

    // হেল্পার ফাংশন: এরর মেসেজ দেখানো
    function showError(input, errorElement, message) {
        input.classList.add('invalid');
        errorElement.innerText = message;
    }

    // হেল্পার ফাংশন: এরর ক্লিয়ার করা
    function clearError(input, errorElement) {
        input.classList.remove('invalid');
        errorElement.innerText = '';
    }

    // ইমেইল প্যাটার্ন ভ্যালিডেশন
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    // মোবাইল নম্বর ভ্যালিডেশন (বাংলাদেশের ১১ ডিজিটের নম্বর)
    function isValidPhone(phone) {
        const re = /^01[3-9]\d{8}$/;
        return re.test(phone.trim());
    }

    // লাইভ ইনপুট ভ্যালিডেশন (ইউজার টাইপ করার সময় এরর চলে যাবে)
    nameInput.addEventListener('input', () => clearError(nameInput, document.getElementById('nameError')));
    emailInput.addEventListener('input', () => clearError(emailInput, document.getElementById('emailError')));
    phoneInput.addEventListener('input', () => clearError(phoneInput, document.getElementById('phoneError')));
    messageInput.addEventListener('input', () => clearError(messageInput, document.getElementById('messageError')));

    // ফর্ম সাবমিট হ্যান্ডলার
    contactForm.addEventListener('submit', function (e) {
        e.preventDefault();
        let isValid = true;

        // নাম ভ্যালিডেশন
        if (nameInput.value.trim() === '') {
            showError(nameInput, document.getElementById('nameError'), 'অনুগ্রহ করে আপনার নাম লিখুন।');
            isValid = false;
        } else if (nameInput.value.trim().length < 3) {
            showError(nameInput, document.getElementById('nameError'), 'নাম অন্তত ৩ অক্ষরের হতে হবে।');
            isValid = false;
        }

        // ইমেইল ভ্যালিডেশন
        if (emailInput.value.trim() === '') {
            showError(emailInput, document.getElementById('emailError'), 'অনুগ্রহ করে ইমেইল লিখুন।');
            isValid = false;
        } else if (!isValidEmail(emailInput.value.trim())) {
            showError(emailInput, document.getElementById('emailError'), 'সঠিক ইমেইল ঠিকানা দিন (e.g. example@mail.com)।');
            isValid = false;
        }

        // ফোন নম্বর ভ্যালিডেশন
        if (phoneInput.value.trim() === '') {
            showError(phoneInput, document.getElementById('phoneError'), 'অনুগ্রহ করে ফোন নম্বর লিখুন।');
            isValid = false;
        } else if (!isValidPhone(phoneInput.value)) {
            showError(phoneInput, document.getElementById('phoneError'), 'সঠিক ১১ ডিজিটের ফোন নম্বর দিন (যেমন: 017XXXXXXXX)।');
            isValid = false;
        }

        // মেসেজ ভ্যালিডেশন
        if (messageInput.value.trim() === '') {
            showError(messageInput, document.getElementById('messageError'), 'আপনার মেসেজটি লিখুন।');
            isValid = false;
        } else if (messageInput.value.trim().length < 10) {
            showError(messageInput, document.getElementById('messageError'), 'মেসেজ অন্তত ১০ অক্ষরের হতে হবে।');
            isValid = false;
        }

        // সব ঠিক থাকলে সাফল্য বার্তা দেখাবে
        if (isValid) {
            formStatus.className = 'form-status success';
            formStatus.innerText = 'ধন্যবাদ! আপনার মেসেজটি সফলভাবে পাঠানো হয়েছে।';
            contactForm.reset();

            // ৫ সেকেন্ড পর মেসেজ মুছে যাবে
            setTimeout(() => {
                formStatus.innerText = '';
            }, 5000);
        } else {
            formStatus.className = 'form-status error';
            formStatus.innerText = 'অনুগ্রহ করে সঠিক তথ্য দিয়ে ফর্মটি পূরণ করুন।';
        }
    });
}
// ==========================================

const loginForm = document.getElementById('loginForm');

if (loginForm) {
    loginForm.addEventListener('submit', function (e) {
        const email = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value.trim();

        if (!email || !password) {
            e.preventDefault();
            alert('ইমেইল এবং পাসওয়ার্ড দিন।');