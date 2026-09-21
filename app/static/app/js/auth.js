function getStorage(key) {
  const raw = localStorage.getItem(key);
  return raw ? JSON.parse(raw) : null;
}

function setStorage(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  const authAlert = document.getElementById('authAlert');
  const registerAlert = document.getElementById('registerAlert');
  const strengthText = document.getElementById('strengthText');
  const passwordInput = document.getElementById('registerPassword');

  function validateEmail(email) {
    return /^\S+@\S+\.\S+$/.test(email);
  }

  function validatePhone(phone) {
    return /^[0-9+\s]{10,15}$/.test(phone);
  }

  function showAlert(element, message, type = 'danger') {
    if (!element) return;
    element.className = `alert alert-${type}`;
    element.textContent = message;
    element.classList.remove('d-none');
  }

  function hideAlert(element) {
    if (!element) return;
    element.classList.add('d-none');
  }

  function calculatePasswordStrength(value) {
    let score = 0;
    if (value.length >= 8) score += 1;
    if (/[A-Z]/.test(value)) score += 1;
    if (/[0-9]/.test(value)) score += 1;
    if (/[^A-Za-z0-9]/.test(value)) score += 1;
    if (score <= 1) return 'Weak';
    if (score === 2 || score === 3) return 'Medium';
    return 'Strong';
  }

  function getUserByIdentifier(identifier) {
    const normalized = identifier.trim().toLowerCase();
    const users = getStorage('users') || [];
    return users.find((item) => {
      const emailMatch = item.email && item.email.toLowerCase() === normalized;
      const phoneMatch = item.phone && item.phone.replace(/\s+/g, '') === normalized.replace(/\s+/g, '');
      return emailMatch || phoneMatch;
    });
  }

  if (passwordInput && strengthText) {
    passwordInput.addEventListener('input', (event) => {
      const strength = calculatePasswordStrength(event.target.value);
      strengthText.textContent = strength;
      strengthText.style.color = strength === 'Strong' ? '#0f5132' : strength === 'Medium' ? '#664d03' : '#842029';
    });
  }

  if (loginForm) {
    loginForm.addEventListener('submit', (event) => {
      event.preventDefault();
      hideAlert(authAlert);
      const identifier = document.getElementById('loginIdentifier').value.trim();
      const password = document.getElementById('loginPassword').value;
      const rememberMe = document.getElementById('rememberMe')?.checked ?? false;

      if (!identifier || !password) {
        showAlert(authAlert, 'Please fill in both fields.');
        return;
      }

      const user = getUserByIdentifier(identifier);
      if (!user || user.password !== password) {
        showAlert(authAlert, 'We could not find an account with that email/phone and password.');
        return;
      }

      const sessionUser = { ...user, rememberMe };
      localStorage.setItem('currentUser', JSON.stringify(sessionUser));
      localStorage.setItem('isLoggedIn', 'true');
      if (rememberMe) {
        localStorage.setItem('rememberedUser', identifier);
      } else {
        localStorage.removeItem('rememberedUser');
      }

      showAlert(authAlert, `Welcome back, ${user.name.split(' ')[0]}!`, 'success');
      setTimeout(() => {
        if (user.role === 'customer') {
          window.location.href = 'designs.html';
        } else if (user.role === 'staff') {
          window.location.href = 'staff/dashboard.html';
        } else if (user.role === 'admin') {
          window.location.href = 'admin/dashboard.html';
        }
      }, 700);
    });
  }

  if (registerForm) {
    registerForm.addEventListener('submit', (event) => {
      event.preventDefault();
      hideAlert(registerAlert);
      const name = document.getElementById('registerName').value.trim();
      const phone = document.getElementById('registerPhone').value.trim();
      const email = document.getElementById('registerEmail').value.trim();
      const password = document.getElementById('registerPassword').value;
      const confirmPassword = document.getElementById('registerConfirmPassword').value;

      if (!name || !phone || !email || !password || !confirmPassword) {
        showAlert(registerAlert, 'Please complete all fields.');
        return;
      }
      if (!validateEmail(email)) {
        showAlert(registerAlert, 'Enter a valid email address.');
        return;
      }
      if (!validatePhone(phone)) {
        showAlert(registerAlert, 'Enter a valid phone number.');
        return;
      }
      if (password !== confirmPassword) {
        showAlert(registerAlert, 'Passwords do not match.');
        return;
      }
      if (password.length < 8) {
        showAlert(registerAlert, 'Password should be at least 8 characters long.');
        return;
      }

      const users = getStorage('users') || [];
      const existingUser = users.find((item) => {
        const sameEmail = item.email && item.email.toLowerCase() === email.toLowerCase();
        const samePhone = item.phone && item.phone.replace(/\s+/g, '') === phone.replace(/\s+/g, '');
        return sameEmail || samePhone;
      });

      if (existingUser) {
        showAlert(registerAlert, 'An account with this email or phone already exists.');
        return;
      }

      const newUser = {
        id: `CUST${String(users.length + 1).padStart(3, '0')}`,
        role: 'customer',
        name,
        email,
        phone,
        password,
        address: '12 Fashion Avenue, Mumbai',
        createdAt: new Date().toISOString(),
      };
      users.push(newUser);
      setStorage('users', users);
      localStorage.setItem('currentUser', JSON.stringify(newUser));
      localStorage.setItem('isLoggedIn', 'true');
      showAlert(registerAlert, 'Account created successfully! Redirecting to designs...', 'success');
      setTimeout(() => {
        window.location.href = 'designs.html';
      }, 900);
    });
  }
});
