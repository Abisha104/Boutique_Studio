const productStorage = window.smartTailorStorage;
const designData = (productStorage && productStorage.getProducts ? productStorage.getProducts() : [
  {
    id: 'silk-lace-blouse',
    name: 'Silk Lace Blouse',
    category: 'Blouse',
    description: 'Soft silk blouse with lace detailing, custom neckline, and premium finish.',
    shortDescription: 'Elegant detailing with a refined finish.',
    price: 1200,
    rating: 4.8,
    image: 'https://images.unsplash.com/photo-1521334884684-d80222895322?auto=format&fit=crop&w=800&q=80',
    available: true,
    sizes: ['S', 'M', 'L', 'XL'],
    colors: ['Ivory', 'Rose', 'Black'],
    fabric: 'Premium Silk',
    deliveryTime: '5-7 days'
  },
  {
    id: 'ivory-bridal-gown',
    name: 'Ivory Bridal Gown',
    category: 'Bridal',
    description: 'Statement bridal couture gown with layered drape, embroidery, and a tailored silhouette.',
    shortDescription: 'Statement bridal styling with couture-inspired details.',
    price: 8200,
    rating: 4.9,
    image: 'https://images.unsplash.com/photo-1503341455253-b2e723bb3dbb?auto=format&fit=crop&w=800&q=80',
    available: true,
    sizes: ['S', 'M', 'L', 'XL'],
    colors: ['Ivory', 'Champagne', 'Pearl'],
    fabric: 'Bridal Satin',
    deliveryTime: '10-14 days'
  },
  {
    id: 'hand-embroidered-kurti',
    name: 'Hand-embroidered Kurti',
    category: 'Kurti',
    description: 'Minimalist kurti with hand embroidery and elegant daily-wear tailoring.',
    shortDescription: 'Modern silhouette with handcrafted character.',
    price: 1800,
    rating: 4.6,
    image: 'https://images.unsplash.com/photo-1521902547894-8f3b6e7b61e8?auto=format&fit=crop&w=800&q=80',
    available: true,
    sizes: ['S', 'M', 'L', 'XL'],
    colors: ['Pearl', 'Moss', 'Charcoal'],
    fabric: 'Cotton Blend',
    deliveryTime: '4-6 days'
  }
]);

const savedFavorites = (window.smartTailorStorage && window.smartTailorStorage.getStorage ? window.smartTailorStorage.getStorage('favorites') : JSON.parse(localStorage.getItem('favorites') || '[]')) || [];
designData.forEach((design) => {
  design.favorite = savedFavorites.includes(design.id);
});

const designGrid = document.getElementById('designGrid');
const noResults = document.getElementById('noResults');
const searchInput = document.getElementById('designSearch');
const filterButtons = document.querySelectorAll('.filter-btn');
const sortSelect = document.getElementById('designSort');

let currentCategory = 'All';
let currentSearch = '';
let currentSort = 'Newest';

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
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => {
    toast.textContent = '';
  }, 2200);
}

function buildCard(design) {
  const card = document.createElement('div');
  card.className = 'col-md-6 col-xl-4';
  card.innerHTML = `
    <article class="design-card shadow-sm">
      <div class="position-relative overflow-hidden">
        <img src="${design.image}" alt="${design.name}" />
        <button class="favorite-btn btn btn-light rounded-circle shadow-sm" data-id="${design.id}" aria-label="Toggle favorite">
          <i class="bi ${design.favorite ? 'bi-heart-fill text-danger' : 'bi-heart'}"></i>
        </button>
      </div>
      <div class="design-body">
        <span class="badge bg-light text-dark mb-2">${design.category}</span>
        <h5>${design.name}</h5>
        <p class="text-muted mb-2">${design.shortDescription || design.description}</p>
        <div class="d-flex justify-content-between align-items-center mb-3">
          <span class="text-gold"><i class="bi bi-star-fill me-1"></i>${design.rating}</span>
          <span class="text-dark fw-semibold">₹${Number(design.price).toLocaleString()}</span>
        </div>
        <div class="d-flex flex-wrap gap-2">
          <button class="btn btn-gold btn-sm rounded-pill add-to-cart-btn" data-product-id="${design.id}">Add to Cart</button>
          <button class="btn btn-outline-dark btn-sm rounded-pill order-now-btn" data-product-id="${design.id}">Order Now</button>
        </div>
        <a href="design-details.html?id=${design.id}" class="btn btn-link text-decoration-none mt-3 p-0">View Details</a>
      </div>
    </article>
  `;

  const favoriteButton = card.querySelector('.favorite-btn');
  favoriteButton.addEventListener('click', () => toggleFavorite(design.id, favoriteButton));

  const addButton = card.querySelector('.add-to-cart-btn');
  addButton.addEventListener('click', () => {
    const result = productStorage.addToCart(design, { quantity: 1 });
    if (!result.success) {
      if (result.requiresLogin) {
        showToast('Please login to add items to your cart.');
        setTimeout(() => { window.location.href = 'login.html'; }, 800);
      } else {
        showToast(result.message || 'Unable to add to cart.');
      }
      return;
    }
    showToast(`${design.name} added to cart.`);
    if (window.smartTailorStorage && window.smartTailorStorage.renderNavbarAuthState) {
      window.smartTailorStorage.renderNavbarAuthState();
    }
  });

  const orderButton = card.querySelector('.order-now-btn');
  orderButton.addEventListener('click', () => {
    if (!productStorage.isLoggedIn()) {
      showToast('Please login to continue.');
      setTimeout(() => { window.location.href = 'login.html'; }, 800);
      return;
    }
    const url = new URL('checkout.html', window.location.href);
    url.searchParams.set('productId', design.id);
    window.location.href = url.toString();
  });

  return card;
}

function renderDesigns() {
  const filtered = designData
    .filter((item) => currentCategory === 'All' || item.category === currentCategory)
    .filter((item) => {
      const query = currentSearch.trim().toLowerCase();
      return !query || item.name.toLowerCase().includes(query) || item.category.toLowerCase().includes(query);
    });

  if (currentSort === 'PriceLow') {
    filtered.sort((a, b) => a.price - b.price);
  } else if (currentSort === 'PriceHigh') {
    filtered.sort((a, b) => b.price - a.price);
  } else if (currentSort === 'Popular') {
    filtered.sort((a, b) => (b.rating || 0) - (a.rating || 0));
  } else {
    filtered.sort((a, b) => b.id.localeCompare(a.id));
  }

  designGrid.innerHTML = '';

  if (!filtered.length) {
    noResults.classList.remove('d-none');
    return;
  }

  noResults.classList.add('d-none');
  filtered.forEach((design) => designGrid.appendChild(buildCard(design)));
}

function toggleFavorite(id, button) {
  const design = designData.find((item) => item.id === id);
  if (!design) return;
  design.favorite = !design.favorite;
  const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
  const updatedFavorites = design.favorite
    ? [...favorites, id].filter((value, index, array) => array.indexOf(value) === index)
    : favorites.filter((item) => item !== id);
  localStorage.setItem('favorites', JSON.stringify(updatedFavorites));
  button.innerHTML = `<i class="bi ${design.favorite ? 'bi-heart-fill text-danger' : 'bi-heart'}"></i>`;
}

if (searchInput) {
  searchInput.addEventListener('input', (event) => {
    currentSearch = event.target.value.trim().toLowerCase();
    renderDesigns();
  });
}

filterButtons.forEach((button) => {
  button.addEventListener('click', () => {
    filterButtons.forEach((btn) => btn.classList.remove('active'));
    button.classList.add('active');
    currentCategory = button.dataset.category;
    renderDesigns();
  });
});

if (sortSelect) {
  sortSelect.addEventListener('change', (event) => {
    currentSort = event.target.value;
    renderDesigns();
  });
}

renderDesigns();
