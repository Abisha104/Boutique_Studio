document.addEventListener('DOMContentLoaded', function () {
  // 1. Counter Animation
  const counters = document.querySelectorAll('.counter');
  counters.forEach((counter) => {
    const target = parseInt(counter.dataset.target, 10);
    const suffix = counter.innerText.includes('+') ? '+' : '';
    const updateCounter = () => {
      const current = parseInt(counter.innerText.replace('+', ''), 10) || 0;
      const increment = target / 80;
      if (current < target) {
        counter.innerText = `${Math.ceil(current + increment)}${suffix}`;
        setTimeout(updateCounter, 16);
      } else {
        counter.innerText = `${target}${suffix}`;
      }
    };
    updateCounter();
  });

  // 2. Header Scroll
  const header = document.querySelector('.site-header');
  if (header) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 20) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    });
  }

  // 3. Django AJAX Form Submission
  const contactForm = document.getElementById('contactForm');
  const contactMessage = document.getElementById('contactMessage');

  if (contactForm) {
    contactForm.addEventListener('submit', async function (event) {
      event.preventDefault();

      const submitButton = contactForm.querySelector('button[type="submit"]');
      const formData = new FormData(contactForm);

      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = 'Sending...';
      }

      try {
        const response = await fetch(contactForm.action || window.location.href, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
          },
        });

        const data = await response.json();

        if (data.status === 'success') {
          contactForm.reset();
          contactMessage.className = 'alert alert-success mt-3';
          contactMessage.innerHTML = `<strong>Success!</strong> ${data.message}`;
        } else {
          contactMessage.className = 'alert alert-danger mt-3';
          contactMessage.innerHTML = `<strong>Error!</strong> ${data.message || 'Please check your inputs.'}`;
        }
      } catch (error) {
        console.error('Submission error:', error);
        contactMessage.className = 'alert alert-danger mt-3';
        contactMessage.innerHTML = '<strong>Error!</strong> Failed to connect to the server. Please try again.';
      } finally {
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.textContent = 'Send Enquiry';
        }
      }
    });
  }
});