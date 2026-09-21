(function () {
  const CART_KEY = 'cart';
  const ORDERS_KEY = 'smartTailorOrders';
  const LEGACY_CART_KEY = 'smartTailorCart';

  function getStorage(key) {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : null;
  }

  function setStorage(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }

  function getCart() {
    const cart = getStorage(CART_KEY) || [];
    return Array.isArray(cart) ? cart : [];
  }

  function setCart(cart) {
    setStorage(CART_KEY, cart);
  }

  function migrateCartStorage() {
    const legacyCart = getStorage(LEGACY_CART_KEY);
    if (!getStorage(CART_KEY) && Array.isArray(legacyCart) && legacyCart.length) {
      setCart(legacyCart);
    }
  }

  function seedDemoCartIfNeeded() {
    if (getStorage(CART_KEY) !== null) return;
    const demoCart = [
      { id: 'D001', name: 'Silk Lace Blouse', category: 'Blouse', price: 1200, image: 'https://images.unsplash.com/photo-1521334884684-d80222895322?auto=format&fit=crop&w=800&q=80', quantity: 1 },
      { id: 'D002', name: 'Ivory Bridal Gown', category: 'Bridal', price: 8200, image: 'https://images.unsplash.com/photo-1503341455253-b2e723bb3dbb?auto=format&fit=crop&w=800&q=80', quantity: 1 },
      { id: 'D003', name: 'Hand-embroidered Kurti', category: 'Kurti', price: 1800, image: 'https://images.unsplash.com/photo-1521902547894-8f3b6e7b61e8?auto=format&fit=crop&w=800&q=80', quantity: 1 },
      { id: 'D004', name: 'Satin Evening Gown', category: 'Gown', price: 5600, image: 'https://images.unsplash.com/photo-1495121605193-b116b5b9c5a6?auto=format&fit=crop&w=800&q=80', quantity: 1 },
    ];
    setCart(demoCart);
  }

  function getCartCount() {
    return getCart().reduce((sum, item) => sum + item.quantity, 0);
  }

  function getCartSubtotal() {
    return getCart().reduce((sum, item) => sum + item.price * item.quantity, 0);
  }

  function updateCartBadge() {
    const cartLink = document.getElementById('cartNavLink');
    if (!cartLink) {
      const actionGroup = document.querySelector('.site-header .d-flex.align-items-center');
      if (!actionGroup) return;
      const existing = document.getElementById('cartNavLink');
      if (existing) return;
      const link = document.createElement('a');
      link.id = 'cartNavLink';
      link.href = 'cart.html';
      link.className = 'btn btn-outline-dark btn-sm rounded-pill position-relative ms-2';
      link.innerHTML = '<i class="bi bi-bag me-2"></i>Cart <span class="badge rounded-pill bg-dark ms-2" id="cartBadge">0</span>';
      actionGroup.appendChild(link);
      return;
    }
    const badge = document.getElementById('cartBadge');
    if (badge) badge.textContent = getCartCount();
  }

  function showToast(message) {
    let toast = document.getElementById('siteToast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'siteToast';
      toast.className = 'position-fixed bottom-0 end-0 m-4 px-3 py-2 rounded-pill bg-dark text-white shadow';
      toast.style.zIndex = '2000';
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    clearTimeout(showToast.timeout);
    showToast.timeout = setTimeout(() => {
      toast.textContent = '';
    }, 2200);
  }

  function addToCart(product) {
    const cart = getCart();
    const existing = cart.find((item) => (item.productId || item.id) === product.id);
    if (existing) {
      existing.quantity += 1;
      existing.subtotal = existing.price * existing.quantity;
    } else {
      cart.push({
        productId: product.id,
        id: product.id,
        name: product.name,
        category: product.category,
        price: Number(product.price),
        image: product.image,
        quantity: 1,
        size: product.sizes?.[0] || 'M',
        color: product.colors?.[0] || 'Default',
        subtotal: Number(product.price),
      });
    }
    setCart(cart);
    updateCartBadge();
    showToast(`${product.name} added to cart`);
  }

  function removeFromCart(productId) {
    const nextCart = getCart().filter((item) => (item.productId || item.id) !== productId);
    setCart(nextCart);
    updateCartBadge();
    renderCartPage();
  }

  function changeQuantity(productId, quantity) {
    const nextCart = getCart().map((item) => {
      if ((item.productId || item.id) !== productId) return item;
      const nextQty = Math.max(1, Number(quantity) || 1);
      return { ...item, quantity: nextQty, subtotal: Number(item.price) * nextQty };
    });
    setCart(nextCart);
    updateCartBadge();
    renderCartPage();
  }

  function clearCart() {
    setCart([]);
    updateCartBadge();
    renderCartPage();
  }

  function placeOrder(formData) {
    const user = JSON.parse(localStorage.getItem('currentUser') || 'null');
    const cart = getCart();
    if (!cart.length || !user) return false;
    const order = {
      id: `ORD${new Date().getTime().toString().slice(-6)}`,
      items: cart,
      customer: formData.customerName || user.name,
      email: formData.email || user.email,
      phone: formData.phone || user.phone,
      address: formData.address || user.address || '12 Fashion Avenue, Mumbai',
      payment: formData.payment || 'Cash on Delivery',
      subtotal: getCartSubtotal(),
      shipping: getCartSubtotal() > 0 ? 120 : 0,
      total: getCartSubtotal() + (getCartSubtotal() > 0 ? 120 : 0),
      createdAt: new Date().toISOString(),
      customerId: user.id,
    };

    const orders = getStorage(ORDERS_KEY) || [];
    orders.unshift(order);
    setStorage(ORDERS_KEY, orders);

    const portalOrders = getStorage('portalOrders') || [];
    portalOrders.unshift({
      id: order.id,
      item: `${cart.length} item(s)`,
      date: new Date().toLocaleDateString(),
      status: 'Order Placed',
      amount: order.total,
      paymentStatus: 'Pending',
      progress: 30,
    });
    setStorage('portalOrders', portalOrders);

    clearCart();
    return order;
  }

  function renderCartPage() {
    const listEl = document.getElementById('cartItems');
    const summaryEl = document.getElementById('cartSummary');
    const emptyEl = document.getElementById('cartEmpty');
    const subtotalEl = document.getElementById('cartSubtotal');
    const shippingEl = document.getElementById('cartShipping');
    const totalEl = document.getElementById('cartTotal');

    if (!listEl && !summaryEl && !emptyEl) return;

    const cart = getCart();
    if (!cart.length) {
      if (listEl) listEl.innerHTML = '';
      if (emptyEl) emptyEl.classList.remove('d-none');
      if (summaryEl) summaryEl.innerHTML = '';
      if (subtotalEl) subtotalEl.textContent = '₹0';
      if (shippingEl) shippingEl.textContent = '₹0';
      if (totalEl) totalEl.textContent = '₹0';
      return;
    }

    if (emptyEl) emptyEl.classList.add('d-none');

    const subtotal = getCartSubtotal();
    const shipping = subtotal > 0 ? 120 : 0;
    const total = subtotal + shipping;

    if (listEl) {
      listEl.innerHTML = cart.map((item) => `
        <div class="cart-card p-4">
          <div class="d-flex justify-content-between gap-3 flex-wrap">
            <div class="d-flex gap-3 align-items-center">
              <img src="${item.image}" alt="${item.name}" class="cart-thumb" />
              <div>
                <h5 class="mb-1">${item.name}</h5>
                <p class="text-muted mb-2">${item.category}</p>
                <p class="fw-semibold mb-0">₹${item.price.toLocaleString()}</p>
              </div>
            </div>
            <div class="d-flex align-items-center gap-2">
              <button class="btn btn-outline-dark btn-sm" data-action="decrease" data-id="${item.id}">-</button>
              <input class="form-control form-control-sm qty-input" type="number" min="1" value="${item.quantity}" data-id="${item.id}" />
              <button class="btn btn-outline-dark btn-sm" data-action="increase" data-id="${item.id}">+</button>
              <button class="btn btn-outline-danger btn-sm ms-2" data-action="remove" data-id="${item.id}"><i class="bi bi-trash"></i></button>
            </div>
          </div>
        </div>
      `).join('');
    }

    if (summaryEl) {
      summaryEl.innerHTML = `
        <div class="cart-summary p-4">
          <h4>Order Summary</h4>
          <div class="d-flex justify-content-between mt-4"><span>Subtotal</span><strong>₹${subtotal.toLocaleString()}</strong></div>
          <div class="d-flex justify-content-between mt-2"><span>Shipping</span><strong>₹${shipping.toLocaleString()}</strong></div>
          <hr />
          <div class="d-flex justify-content-between"><span>Total</span><strong>₹${total.toLocaleString()}</strong></div>
          <a href="checkout.html" class="btn btn-gold w-100 mt-4">Proceed to Checkout</a>
        </div>
      `;
    }

    const checkoutSummary = document.getElementById('checkoutSummary');
    if (checkoutSummary) {
      checkoutSummary.innerHTML = `
        <div class="d-flex justify-content-between py-2"><span>Subtotal</span><strong>₹${subtotal.toLocaleString()}</strong></div>
        <div class="d-flex justify-content-between py-2"><span>Shipping</span><strong>₹${shipping.toLocaleString()}</strong></div>
        <hr />
        <div class="d-flex justify-content-between py-2"><span>Total</span><strong>₹${total.toLocaleString()}</strong></div>
        <ul class="list-unstyled mt-3">
          ${cart.map((item) => `<li class="mb-2">${item.name} × ${item.quantity}</li>`).join('')}
        </ul>
      `;
    }

    if (subtotalEl) subtotalEl.textContent = `₹${subtotal.toLocaleString()}`;
    if (shippingEl) shippingEl.textContent = `₹${shipping.toLocaleString()}`;
    if (totalEl) totalEl.textContent = `₹${total.toLocaleString()}`;
  }

  function attachCartEvents() {
    document.addEventListener('click', (event) => {
      const button = event.target.closest('[data-action]');
      if (!button) return;
      const id = button.getAttribute('data-id');
      if (button.getAttribute('data-action') === 'remove') {
        removeFromCart(id);
      } else if (button.getAttribute('data-action') === 'increase') {
        changeQuantity(id, getCart().find((item) => item.id === id)?.quantity + 1 || 1);
      } else if (button.getAttribute('data-action') === 'decrease') {
        const item = getCart().find((item) => item.id === id);
        if (item && item.quantity > 1) {
          changeQuantity(id, item.quantity - 1);
        }
      }
    });

    document.addEventListener('input', (event) => {
      const input = event.target.closest('.qty-input');
      if (!input) return;
      changeQuantity(input.getAttribute('data-id'), parseInt(input.value, 10) || 1);
    });

    document.querySelectorAll('.add-to-cart-btn').forEach((button) => {
      button.addEventListener('click', () => {
        const product = JSON.parse(button.getAttribute('data-product'));
        addToCart(product);
      });
    });

    const checkoutForm = document.getElementById('checkoutForm');
    if (checkoutForm) {
      checkoutForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const formData = new FormData(checkoutForm);
        const order = placeOrder({
          customerName: formData.get('customerName')?.toString().trim(),
          email: formData.get('email')?.toString().trim(),
          phone: formData.get('phone')?.toString().trim(),
          address: formData.get('address')?.toString().trim(),
          payment: formData.get('payment')?.toString().trim(),
        });
        if (!order) {
          document.getElementById('checkoutMessage').innerHTML = '<div class="alert alert-danger">Your cart is empty.</div>';
          return;
        }
        checkoutForm.reset();
        document.getElementById('checkoutMessage').innerHTML = `<div class="alert alert-success">Order placed successfully! Your order ID is <strong>${order.id}</strong>.</div>`;
        window.location.href = 'customer/dashboard.html';
      });
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    migrateCartStorage();
    seedDemoCartIfNeeded();
    updateCartBadge();
    attachCartEvents();
    renderCartPage();

    const detailName = document.getElementById('detailName');
    const detailCategory = document.getElementById('detailCategory');
    const detailPrice = document.getElementById('detailPrice');
    const detailDescription = document.getElementById('detailDescription');
    const detailImage = document.getElementById('mainDesignImage');
    const addToCartButton = document.getElementById('detailAddToCart');

    const params = new URLSearchParams(window.location.search);
    const productId = params.get('id');
    const product = productId ? (window.smartTailorStorage ? window.smartTailorStorage.getProductById(productId) : null) : null;

    if (detailName && product) {
      detailName.textContent = product.name;
      detailCategory.textContent = product.category;
      detailPrice.textContent = `₹${product.price.toLocaleString()}`;
      detailDescription.textContent = product.description || 'A premium bespoke piece crafted with precise tailoring and luxurious finish.';
      if (detailImage) detailImage.src = product.image;
      if (addToCartButton) {
        addToCartButton.setAttribute('data-product', JSON.stringify(product));
        addToCartButton.classList.add('add-to-cart-btn');
      }
    }

    if (addToCartButton && product) {
      addToCartButton.addEventListener('click', () => {
        const result = (window.smartTailorStorage || window.smartTailorShop).addToCart(product, { quantity: 1 });
        if (!result.success) {
          showToast(result.message || 'Unable to add item to cart.');
          if (result.requiresLogin) {
            setTimeout(() => { window.location.href = 'login.html'; }, 800);
          }
          return;
        }
        showToast(`${product.name} added to cart.`);
      });
    }
  });

  window.smartTailorShop = {
    addToCart,
    getCart,
    getCartCount,
    getCartSubtotal,
    clearCart,
    placeOrder,
  };
})();
