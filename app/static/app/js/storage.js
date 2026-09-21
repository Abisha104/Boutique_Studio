(function () {
  const DEFAULT_PRODUCTS = [
    {
      id: 'silk-lace-blouse',
      name: 'Silk Lace Blouse',
      category: 'Blouse',
      description: 'Soft silk blouse with lace detailing, custom neckline, and premium finish.',
      shortDescription: 'Elegant detailing with a refined finish.',
      price: 1200,
      image: 'https://images.unsplash.com/photo-1521334884684-d80222895322?auto=format&fit=crop&w=800&q=80',
      rating: 4.8,
      available: true,
      sizes: ['S', 'M', 'L', 'XL'],
      colors: ['Ivory', 'Rose', 'Black'],
      fabric: 'Premium Silk',
      deliveryTime: '5-7 days',
    },
    {
      id: 'ivory-bridal-gown',
      name: 'Ivory Bridal Gown',
      category: 'Bridal',
      description: 'Statement bridal couture gown with layered drape, embroidery, and a tailored silhouette.',
      shortDescription: 'Statement bridal styling with couture-inspired details.',
      price: 8200,
      image: 'https://images.unsplash.com/photo-1503341455253-b2e723bb3dbb?auto=format&fit=crop&w=800&q=80',
      rating: 4.9,
      available: true,
      sizes: ['S', 'M', 'L', 'XL'],
      colors: ['Ivory', 'Champagne', 'Pearl'],
      fabric: 'Bridal Satin',
      deliveryTime: '10-14 days',
    },
    {
      id: 'hand-embroidered-kurti',
      name: 'Hand-embroidered Kurti',
      category: 'Kurti',
      description: 'Minimalist kurti with hand embroidery and elegant daily-wear tailoring.',
      shortDescription: 'Modern silhouette with handcrafted character.',
      price: 1800,
      image: 'https://images.unsplash.com/photo-1521902547894-8f3b6e7b61e8?auto=format&fit=crop&w=800&q=80',
      rating: 4.6,
      available: true,
      sizes: ['S', 'M', 'L', 'XL'],
      colors: ['Pearl', 'Moss', 'Charcoal'],
      fabric: 'Cotton Blend',
      deliveryTime: '4-6 days',
    },
    {
      id: 'satin-evening-gown',
      name: 'Satin Evening Gown',
      category: 'Gown',
      description: 'Graceful evening gown with fluid satin layers and custom draping.',
      shortDescription: 'Graceful evening styling with fluid satin layers.',
      price: 5600,
      image: 'https://images.unsplash.com/photo-1495121605193-b116b5b9c5a6?auto=format&fit=crop&w=800&q=80',
      rating: 4.7,
      available: true,
      sizes: ['S', 'M', 'L', 'XL'],
      colors: ['Midnight', 'Rose', 'Ivory'],
      fabric: 'Premium Satin',
      deliveryTime: '7-9 days',
    },
    {
      id: 'pearl-chudidar-set',
      name: 'Pearl Chudidar Set',
      category: 'Chudidar',
      description: 'Classic chudidar set with articulated fit and polished finishing.',
      shortDescription: 'Classic chudidar set with polished tailoring.',
      price: 1600,
      image: 'https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=800&q=80',
      rating: 4.5,
      available: true,
      sizes: ['XS', 'S', 'M', 'L', 'XL'],
      colors: ['Coffee', 'Taupe', 'Black'],
      fabric: 'Cotton Twill',
      deliveryTime: '3-5 days',
    },
    {
      id: 'floral-kids-frock',
      name: 'Floral Kids Frock',
      category: 'Kids Wear',
      description: 'Comfort-focused party frock with breathable fabric and easy movement.',
      shortDescription: 'Comfort-focused party frock with cheerful detailing.',
      price: 950,
      image: 'https://images.unsplash.com/photo-1504198458649-3128b932f49b?auto=format&fit=crop&w=800&q=80',
      rating: 4.4,
      available: true,
      sizes: ['4Y', '6Y', '8Y', '10Y'],
      colors: ['Floral Pink', 'Sky Blue', 'Mint'],
      fabric: 'Breathable Cotton',
      deliveryTime: '3-4 days',
    },
    {
      id: 'luxury-lehenga-set',
      name: 'Luxury Lehenga Set',
      category: 'Bridal',
      description: 'Rich festive bridal lehenga with heavy embroidery and premium finish.',
      shortDescription: 'Rich festive bridal lehenga with premium finish.',
      price: 9800,
      image: 'https://images.unsplash.com/photo-1617038260897-41a1f14a8ca0?auto=format&fit=crop&w=800&q=80',
      rating: 4.95,
      available: true,
      sizes: ['S', 'M', 'L', 'XL'],
      colors: ['Wine', 'Ivory', 'Gold'],
      fabric: 'Premium Brocade',
      deliveryTime: '12-15 days',
    },
    {
      id: 'crafted-anarkali-suit',
      name: 'Crafted Anarkali Suit',
      category: 'Kurti',
      description: 'Elegant anarkali with pleated flow and tailored elegance.',
      shortDescription: 'Elegant anarkali with pleated flow and refined finish.',
      price: 2400,
      image: 'https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=800&q=80',
      rating: 4.7,
      available: true,
      sizes: ['S', 'M', 'L', 'XL'],
      colors: ['Maroon', 'Teal', 'Beige'],
      fabric: 'Georgette',
      deliveryTime: '5-7 days',
    },
    {
      id: 'designer-party-saree',
      name: 'Designer Party Saree',
      category: 'Gown',
      description: 'Festive saree with premium drape and decorative detailing.',
      shortDescription: 'Festive saree with premium drape and detailing.',
      price: 4100,
      image: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80',
      rating: 4.6,
      available: true,
      sizes: ['Free Size'],
      colors: ['Deep Plum', 'Emerald', 'Saffron'],
      fabric: 'Silk Blend',
      deliveryTime: '6-8 days',
    },
    {
      id: 'modern-indo-western-coat',
      name: 'Modern Indo-Western Coat',
      category: 'Blouse',
      description: 'Stylish fusion coat with strong tailoring and premium structure.',
      shortDescription: 'Stylish fusion coat with tailored structure.',
      price: 3100,
      image: 'https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=800&q=80',
      rating: 4.8,
      available: true,
      sizes: ['S', 'M', 'L', 'XL'],
      colors: ['Black', 'Sand', 'Forest'],
      fabric: 'Wool Blend',
      deliveryTime: '7-10 days',
    },
    {
      id: 'peacock-festive-dress',
      name: 'Peacock Festive Dress',
      category: 'Kids Wear',
      description: 'Bright festive wear for kids with premium comfort and charm.',
      shortDescription: 'Bright festive wear for kids with premium comfort.',
      price: 1350,
      image: 'https://images.unsplash.com/photo-1516627145497-ae6968895b74?auto=format&fit=crop&w=800&q=80',
      rating: 4.3,
      available: true,
      sizes: ['4Y', '6Y', '8Y', '10Y'],
      colors: ['Peacock', 'Coral', 'Lilac'],
      fabric: 'Soft Rayon',
      deliveryTime: '4-5 days',
    },
    {
      id: 'classic-pant-set',
      name: 'Classic Pant Set',
      category: 'Chudidar',
      description: 'Polished pant set with structured tailoring and elegant comfort.',
      shortDescription: 'Polished pant set with structured tailoring.',
      price: 2200,
      image: 'https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=800&q=80',
      rating: 4.6,
      available: true,
      sizes: ['S', 'M', 'L', 'XL'],
      colors: ['Stone', 'Navy', 'Olive'],
      fabric: 'Stretch Cotton',
      deliveryTime: '5-7 days',
    }
  ];

  function getStorage(key) {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : null;
  }

  function setStorage(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }

  function getCurrentUser() {
    return getStorage('currentUser');
  }

  function isLoggedIn() {
    return localStorage.getItem('isLoggedIn') === 'true' || !!getCurrentUser();
  }

  function setCurrentUser(user) {
    if (!user) {
      localStorage.removeItem('currentUser');
      localStorage.removeItem('isLoggedIn');
      return;
    }
    setStorage('currentUser', user);
    localStorage.setItem('isLoggedIn', 'true');
  }

  function getProducts() {
    const savedProducts = getStorage('catalogProducts');
    if (savedProducts && Array.isArray(savedProducts) && savedProducts.length) {
      return savedProducts;
    }
    setStorage('catalogProducts', DEFAULT_PRODUCTS);
    return DEFAULT_PRODUCTS;
  }

  function getProductById(id) {
    return getProducts().find((product) => product.id === id) || null;
  }

  function getCustomerCartKey() {
    const user = getCurrentUser();
    return user && user.id ? `cart_${user.id}` : 'cart_guest';
  }

  function getCart() {
    const cart = getStorage(getCustomerCartKey()) || [];
    return Array.isArray(cart) ? cart : [];
  }

  function setCart(cart) {
    setStorage(getCustomerCartKey(), cart);
    notifyCartUpdated();
  }

  function getCartCount() {
    return getCart().reduce((sum, item) => sum + (Number(item.quantity) || 1), 0);
  }

  function getCartSubtotal() {
    return getCart().reduce((sum, item) => sum + ((Number(item.price) || 0) * (Number(item.quantity) || 1)), 0);
  }

  function notifyCartUpdated() {
    window.dispatchEvent(new CustomEvent('cartUpdated'));
  }

  function addToCart(product, selectedOptions = {}) {
    if (!product || !product.id) return { success: false, message: 'Invalid product.' };
    if (!isLoggedIn()) {
      return {
        success: false,
        requiresLogin: true,
        message: 'Please login to add items to your cart.'
      };
    }

    const cart = getCart();
    const key = `${product.id}-${selectedOptions.size || 'default'}-${selectedOptions.color || 'default'}`;
    const existingIndex = cart.findIndex((item) => `${item.productId || item.id}-${item.size || 'default'}-${item.color || 'default'}` === key);

    if (existingIndex >= 0) {
      cart[existingIndex].quantity += Number(selectedOptions.quantity) || 1;
    } else {
      cart.push({
        productId: product.id,
        id: product.id,
        name: product.name,
        category: product.category,
        price: Number(product.price),
        image: product.image,
        quantity: Number(selectedOptions.quantity) || 1,
        size: selectedOptions.size || product.sizes?.[0] || 'M',
        color: selectedOptions.color || product.colors?.[0] || 'Default',
        fabric: selectedOptions.fabric || product.fabric || '',
        subtotal: Number(product.price) * (Number(selectedOptions.quantity) || 1),
      });
    }

    const updatedCart = cart.map((item) => ({
      ...item,
      subtotal: Number(item.price) * Number(item.quantity)
    }));

    setCart(updatedCart);
    return { success: true, message: `${product.name} added to cart.` };
  }

  function removeFromCart(productId) {
    const cart = getCart().filter((item) => (item.productId || item.id) !== productId);
    setCart(cart);
    return cart;
  }

  function updateCartQuantity(productId, quantity) {
    const cart = getCart().map((item) => {
      if ((item.productId || item.id) !== productId) return item;
      const nextQuantity = Math.max(1, Number(quantity) || 1);
      return { ...item, quantity: nextQuantity, subtotal: Number(item.price) * nextQuantity };
    });
    setCart(cart);
    return cart;
  }

  function clearCart() {
    setCart([]);
  }

  function getOrders() {
    const user = getCurrentUser();
    if (!user) return [];
    const orders = getStorage(`orders_${user.id}`) || [];
    return Array.isArray(orders) ? orders : [];
  }

  function setOrders(orders) {
    const user = getCurrentUser();
    if (!user) return;
    setStorage(`orders_${user.id}`, orders);
  }

  function createOrder(orderPayload) {
    const order = {
      orderId: `ST-${new Date().getFullYear()}-${String(Math.floor(Math.random() * 9000) + 1000)}`,
      customerId: orderPayload.customerId || getCurrentUser()?.id,
      customerName: orderPayload.customerName || getCurrentUser()?.name,
      customerEmail: orderPayload.customerEmail || getCurrentUser()?.email,
      items: orderPayload.items || [],
      totalAmount: Number(orderPayload.totalAmount) || 0,
      measurements: orderPayload.measurements || {},
      status: 'Order Placed',
      paymentStatus: orderPayload.paymentStatus || 'Pending',
      createdAt: new Date().toISOString(),
      shippingAddress: orderPayload.shippingAddress || '',
      phone: orderPayload.phone || getCurrentUser()?.phone || '',
    };

    const allOrders = getOrders();
    allOrders.unshift(order);
    setOrders(allOrders);
    return order;
  }

  function getMeasurements() {
    const user = getCurrentUser();
    if (!user) return {};
    const key = `measurements_${user.id}`;
    return getStorage(key) || {};
  }

  function saveMeasurements(measurements) {
    const user = getCurrentUser();
    if (!user) return null;
    const saved = { ...getMeasurements(), ...measurements };
    setStorage(`measurements_${user.id}`, saved);
    return saved;
  }

  function initDemoStorage() {
    if (!getStorage('users')) {
      setStorage('users', [
        {
          id: 'CUST001',
          role: 'customer',
          name: 'Abisha Sharma',
          email: 'customer@example.com',
          phone: '+91 98765 43210',
          password: 'customer123',
          address: '12 Fashion Avenue, Mumbai',
        },
        {
          id: 'STF001',
          role: 'staff',
          name: 'Sarah Joseph',
          email: 'staff@smarttailor.com',
          phone: '+91 99876 54321',
          password: 'staff123',
        },
        {
          id: 'ADMIN001',
          role: 'admin',
          name: 'Admin User',
          email: 'admin@example.com',
          phone: '+91 99000 12345',
          password: 'admin123',
        },
      ]);
    }

    if (!getStorage('favorites')) {
      setStorage('favorites', []);
    }

    if (!getStorage(getCustomerCartKey())) {
      setStorage(getCustomerCartKey(), []);
    }

    if (!getStorage('consultationRequests')) {
      setStorage('consultationRequests', []);
    }

    if (!getStorage('catalogProducts')) {
      setStorage('catalogProducts', DEFAULT_PRODUCTS);
    }
  }

  function renderNavbarAuthState() {
    const user = getCurrentUser();
    const loggedIn = isLoggedIn();
    const loginBtn = document.getElementById('loginNavBtn');
    const accountBtn = document.getElementById('accountNavBtn');
    const ordersBtn = document.getElementById('ordersNavBtn');
    const logoutBtn = document.getElementById('logoutNavBtn');
    const cartBadge = document.getElementById('cartCountBadge');

    if (loginBtn) loginBtn.style.display = loggedIn ? 'none' : 'inline-flex';
    if (accountBtn) accountBtn.style.display = loggedIn ? 'inline-flex' : 'none';
    if (ordersBtn) ordersBtn.style.display = loggedIn ? 'inline-flex' : 'none';
    if (logoutBtn) logoutBtn.style.display = loggedIn ? 'inline-flex' : 'none';

    if (user && accountBtn) {
      const firstName = user.name?.split(' ')[0] || 'Account';
      accountBtn.innerHTML = `<i class="bi bi-person me-1"></i>${firstName}`;
    }

    if (cartBadge) {
      cartBadge.textContent = getCartCount();
    }
  }

  function bindAuthActions() {
    document.querySelectorAll('.logout-link').forEach((link) => {
      link.addEventListener('click', (event) => {
        event.preventDefault();
        localStorage.removeItem('currentUser');
        localStorage.removeItem('isLoggedIn');
        renderNavbarAuthState();
        window.location.href = window.location.pathname.includes('/customer/') ? '../index.html' : 'index.html';
      });
    });
  }

  initDemoStorage();

  document.addEventListener('DOMContentLoaded', () => {
    renderNavbarAuthState();
    bindAuthActions();
    const currentUser = getCurrentUser();
    const currentPath = window.location.pathname;
    const isCustomerPage = currentPath.includes('/customer/');

    if (currentUser && (currentPath.endsWith('/login.html') || currentPath.endsWith('/register.html'))) {
      window.location.replace(isCustomerPage ? '../designs.html' : 'designs.html');
      return;
    }

    const authLinks = Array.from(document.querySelectorAll('[data-auth-link="true"]'));
    authLinks.forEach((link) => {
      if (currentUser) {
        const firstName = currentUser.name?.split(' ')[0] || 'Account';
        link.textContent = `Hi, ${firstName}`;
        link.setAttribute('href', isCustomerPage ? '../customer/dashboard.html' : 'customer/dashboard.html');
      } else {
        link.textContent = 'Login';
        link.setAttribute('href', isCustomerPage ? '../login.html' : 'login.html');
      }
    });

    window.addEventListener('cartUpdated', renderNavbarAuthState);
  });

  window.smartTailorStorage = {
    getStorage,
    setStorage,
    getCurrentUser,
    isLoggedIn,
    setCurrentUser,
    getProducts,
    getProductById,
    getCart,
    setCart,
    getCartCount,
    getCartSubtotal,
    addToCart,
    removeFromCart,
    updateCartQuantity,
    clearCart,
    getOrders,
    setOrders,
    createOrder,
    getMeasurements,
    saveMeasurements,
    renderNavbarAuthState,
    initDemoStorage,
    notifyCartUpdated,
    getCustomerCartKey,
  };
})();
