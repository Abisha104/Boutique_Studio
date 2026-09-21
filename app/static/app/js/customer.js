document.addEventListener('DOMContentLoaded', () => {
  const currentUser = JSON.parse(localStorage.getItem('currentUser'));
  if (!currentUser || currentUser.role !== 'customer') {
    document.body.innerHTML = `<div class="d-flex align-items-center justify-content-center min-vh-100 bg-light"><div class="text-center"><h1>Access Denied</h1><p class="lead">You do not have permission to access this page.</p><a href="../login.html" class="btn btn-gold mt-3">Return to Login</a></div></div>`;
    return;
  }

  function ensurePortalData() {
    if (!getStorage('portalOrders')) {
      setStorage('portalOrders', [
        { id: 'ORD1001', item: 'Silk Lace Blouse', date: '2026-08-05', status: 'Ready for pickup', amount: 1200, paymentStatus: 'Paid', progress: 90 },
        { id: 'ORD1002', item: 'Ivory Bridal Gown', date: '2026-08-02', status: 'In stitching', amount: 8200, paymentStatus: 'Pending', progress: 60 },
        { id: 'ORD1003', item: 'Hand-embroidered Kurti', date: '2026-07-22', status: 'Delivered', amount: 1800, paymentStatus: 'Paid', progress: 100 },
      ]);
    }

    if (!getStorage('portalMeasurements')) {
      setStorage('portalMeasurements', {
        bust: '34',
        waist: '28',
        hips: '36',
        shoulder: '16',
        sleeve: '24',
      });
    }

    if (!getStorage('portalNotifications')) {
      setStorage('portalNotifications', [
        { id: 1, text: 'Your final blouse fitting is confirmed for tomorrow.', read: false },
        { id: 2, text: 'A new fabric option has been added to your bridal order.', read: true },
      ]);
    }

    if (!getStorage('portalFeedback')) {
      setStorage('portalFeedback', [
        { id: 1, title: 'Excellent finish', message: 'The stitching quality and delivery were both impressive.', author: 'Aisha' },
      ]);
    }
  }

  ensurePortalData();

  const welcomeName = document.getElementById('customerName');
  const totalOrders = document.getElementById('totalOrders');
  const activeOrders = document.getElementById('activeOrders');
  const completedOrders = document.getElementById('completedOrders');
  const pendingPayment = document.getElementById('pendingPayment');
  const profileName = document.getElementById('profileName');
  const profileEmail = document.getElementById('profileEmail');
  const profilePhone = document.getElementById('profilePhone');
  const detailName = document.getElementById('detailName');
  const detailEmail = document.getElementById('detailEmail');
  const detailPhone = document.getElementById('detailPhone');
  const detailAddress = document.getElementById('detailAddress');
  const editName = document.getElementById('editName');
  const editEmail = document.getElementById('editEmail');
  const editPhone = document.getElementById('editPhone');
  const editAddress = document.getElementById('editAddress');
  const editProfileForm = document.getElementById('editProfileForm');
  const latestList = document.getElementById('latestActivityList');
  const measurementForm = document.getElementById('measurementsForm');
  const measurementsMsg = document.getElementById('measurementsMessage');
  const ordersList = document.getElementById('ordersList');
  const trackingList = document.getElementById('trackingList');
  const paymentsList = document.getElementById('paymentsList');
  const invoicesList = document.getElementById('invoicesList');
  const notificationsList = document.getElementById('notificationsList');
  const favoritesList = document.getElementById('favoritesList');
  const feedbackList = document.getElementById('feedbackList');
  const feedbackForm = document.getElementById('feedbackForm');
  const feedbackMessage = document.getElementById('feedbackMessage');

  if (welcomeName) {
    welcomeName.textContent = `Welcome back, ${currentUser.name.split(' ')[0]} 👋`;
  }

  const orders = getStorage('portalOrders') || [];
  const pendingAmount = orders.filter((order) => order.paymentStatus === 'Pending').reduce((sum, order) => sum + order.amount, 0);

  if (totalOrders) totalOrders.textContent = orders.length;
  if (activeOrders) activeOrders.textContent = orders.filter((order) => order.status !== 'Delivered').length;
  if (completedOrders) completedOrders.textContent = orders.filter((order) => order.status === 'Delivered').length;
  if (pendingPayment) pendingPayment.textContent = `₹${pendingAmount.toLocaleString()}`;

  if (profileName) profileName.textContent = currentUser.name;
  if (profileEmail) profileEmail.textContent = currentUser.email;
  if (profilePhone) profilePhone.textContent = currentUser.phone;
  if (detailName) detailName.textContent = currentUser.name;
  if (detailEmail) detailEmail.textContent = currentUser.email;
  if (detailPhone) detailPhone.textContent = currentUser.phone;
  if (detailAddress) detailAddress.textContent = currentUser.address || '12 Fashion Avenue, Mumbai';

  if (editName) editName.value = currentUser.name;
  if (editEmail) editEmail.value = currentUser.email;
  if (editPhone) editPhone.value = currentUser.phone;
  if (editAddress) editAddress.value = currentUser.address || '12 Fashion Avenue, Mumbai';

  if (latestList) {
    latestList.innerHTML = orders.slice(0, 3).map((order) => `<li><i class="bi bi-check-circle-fill text-success me-2"></i>${order.item} · ${order.status}</li>`).join('');
  }

  if (editProfileForm) {
    editProfileForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const users = getStorage('users') || [];
      const updatedUser = {
        ...currentUser,
        name: editName.value.trim(),
        email: editEmail.value.trim(),
        phone: editPhone.value.trim(),
        address: editAddress.value.trim(),
      };
      const userIndex = users.findIndex((user) => user.id === currentUser.id);
      if (userIndex !== -1) {
        users[userIndex] = updatedUser;
        setStorage('users', users);
        localStorage.setItem('currentUser', JSON.stringify(updatedUser));
        location.reload();
      }
    });
  }

  if (measurementForm) {
    const measurements = getStorage('portalMeasurements') || {};
    Object.entries(measurements).forEach(([key, value]) => {
      const input = document.getElementById(key);
      if (input) {
        input.value = value;
      }
    });

    measurementForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const formData = new FormData(measurementForm);
      const nextMeasurements = Object.fromEntries(formData.entries());
      setStorage('portalMeasurements', nextMeasurements);
      if (measurementsMsg) {
        measurementsMsg.className = 'alert alert-success mt-3';
        measurementsMsg.textContent = 'Your measurement profile has been updated successfully.';
      }
    });
  }

  if (ordersList) {
    ordersList.innerHTML = orders.length
      ? orders.map((order) => `
        <div class="section-card p-4">
          <div class="d-flex justify-content-between align-items-start gap-3 flex-wrap">
            <div>
              <h5 class="mb-1">${order.item}</h5>
              <p class="text-muted mb-2">Order ${order.id} · ${order.date}</p>
              <span class="status-badge">${order.status}</span>
            </div>
            <div class="text-end">
              <p class="fw-semibold mb-1">₹${order.amount.toLocaleString()}</p>
              <p class="small text-muted">${order.paymentStatus}</p>
            </div>
          </div>
        </div>`).join('')
      : '<div class="empty-state">You have no orders yet. Start with a new design to see it here.</div>';
  }

  if (trackingList) {
    trackingList.innerHTML = orders.map((order) => `
      <div class="section-card p-4">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
          <div>
            <h5 class="mb-1">${order.id}</h5>
            <p class="text-muted mb-0">${order.item}</p>
          </div>
          <span class="status-badge">${order.status}</span>
        </div>
        <div class="progress mt-3" style="height: 8px;">
          <div class="progress-bar bg-gold" role="progressbar" style="width: ${order.progress}%"></div>
        </div>
      </div>`).join('');
  }

  if (paymentsList) {
    paymentsList.innerHTML = orders.map((order) => `
      <div class="section-card p-4">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
          <div>
            <h5 class="mb-1">${order.id}</h5>
            <p class="text-muted mb-0">${order.item}</p>
          </div>
          <div class="text-end">
            <p class="fw-semibold mb-1">₹${order.amount.toLocaleString()}</p>
            <span class="status-badge">${order.paymentStatus}</span>
          </div>
        </div>
      </div>`).join('');
  }

  if (invoicesList) {
    invoicesList.innerHTML = orders.map((order) => `
      <div class="section-card p-4">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
          <div>
            <h5 class="mb-1">INV-${order.id.replace('ORD', '')}</h5>
            <p class="text-muted mb-0">${order.item}</p>
          </div>
          <button class="btn btn-outline-dark btn-sm">Download PDF</button>
        </div>
      </div>`).join('');
  }

  if (notificationsList) {
    const notifications = getStorage('portalNotifications') || [];
    notificationsList.innerHTML = notifications.map((item) => `
      <div class="section-card p-4 ${item.read ? '' : 'border border-warning'}">
        <div class="d-flex justify-content-between align-items-start gap-2">
          <p class="mb-0">${item.text}</p>
          <span class="status-badge">${item.read ? 'Read' : 'New'}</span>
        </div>
      </div>`).join('');
  }

  if (favoritesList) {
    const favorites = getStorage('favorites') || [];
    const favoriteDesigns = [
      { id: 'D001', name: 'Silk Lace Blouse', price: 1200 },
      { id: 'D002', name: 'Ivory Bridal Gown', price: 8200 },
      { id: 'D003', name: 'Hand-embroidered Kurti', price: 1800 },
    ].filter((design) => favorites.includes(design.id));

    favoritesList.innerHTML = favoriteDesigns.length
      ? favoriteDesigns.map((design) => `
        <div class="section-card p-4">
          <h5>${design.name}</h5>
          <p class="text-muted mb-3">₹${design.price.toLocaleString()}</p>
          <a href="../design-details.html" class="btn btn-outline-dark btn-sm">View Design</a>
        </div>`).join('')
      : '<div class="empty-state">You have no favourite designs yet. Save some from the designs page.</div>';
  }

  if (feedbackForm && feedbackList) {
    const feedbackEntries = getStorage('portalFeedback') || [];
    feedbackList.innerHTML = feedbackEntries.map((item) => `
      <div class="section-card p-4">
        <h5>${item.title}</h5>
        <p class="text-muted mb-2">${item.message}</p>
        <small class="text-muted">— ${item.author}</small>
      </div>`).join('');

    feedbackForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const formData = new FormData(feedbackForm);
      const newFeedback = {
        id: Date.now(),
        title: formData.get('title').toString().trim(),
        message: formData.get('message').toString().trim(),
        author: currentUser.name.split(' ')[0],
      };
      const nextFeedback = [newFeedback, ...feedbackEntries];
      setStorage('portalFeedback', nextFeedback);
      feedbackForm.reset();
      if (feedbackMessage) {
        feedbackMessage.className = 'alert alert-success mt-3';
        feedbackMessage.textContent = 'Thanks for your feedback. It has been saved.';
      }
      feedbackList.innerHTML = nextFeedback.map((item) => `
        <div class="section-card p-4">
          <h5>${item.title}</h5>
          <p class="text-muted mb-2">${item.message}</p>
          <small class="text-muted">— ${item.author}</small>
        </div>`).join('');
    });
  }
});
