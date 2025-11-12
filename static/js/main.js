// ===================================
// MAIN JAVASCRIPT - PORTFOLIO
// ===================================

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", function () {
  initNavigation();
  initScrollProgress();
  initBackToTop();
  initAOS();
  initFormValidation();
  initSmoothScroll();
});

// ===================================
// NAVIGATION
// ===================================
function initNavigation() {
  const mobileMenuBtn = document.getElementById("mobile-menu-btn");
  const mobileMenu = document.getElementById("mobile-menu");
  const navbar = document.getElementById("navbar");

  // Mobile menu toggle
  if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener("click", function () {
      mobileMenu.classList.toggle("hidden");
      const icon = this.querySelector("i");
      icon.classList.toggle("fa-bars");
      icon.classList.toggle("fa-times");
    });

    // Close mobile menu when clicking outside
    document.addEventListener("click", function (event) {
      const isClickInside =
        mobileMenuBtn.contains(event.target) ||
        mobileMenu.contains(event.target);
      if (!isClickInside && !mobileMenu.classList.contains("hidden")) {
        mobileMenu.classList.add("hidden");
        const icon = mobileMenuBtn.querySelector("i");
        icon.classList.add("fa-bars");
        icon.classList.remove("fa-times");
      }
    });
  }

  // Navbar scroll effect
  let lastScroll = 0;
  window.addEventListener("scroll", function () {
    const currentScroll = window.pageYOffset;

    if (currentScroll <= 0) {
      navbar.classList.remove("shadow-lg");
    } else {
      navbar.classList.add("shadow-lg");
    }

    // Hide/show navbar on scroll
    if (currentScroll > lastScroll && currentScroll > 100) {
      navbar.style.transform = "translateY(-100%)";
    } else {
      navbar.style.transform = "translateY(0)";
    }

    lastScroll = currentScroll;
  });
}

// ===================================
// SCROLL PROGRESS BAR
// ===================================
function initScrollProgress() {
  const progressBar = document.getElementById("scroll-progress");

  if (progressBar) {
    window.addEventListener("scroll", function () {
      const windowHeight =
        document.documentElement.scrollHeight -
        document.documentElement.clientHeight;
      const scrolled = (window.pageYOffset / windowHeight) * 100;
      progressBar.style.width = scrolled + "%";
    });
  }
}

// ===================================
// BACK TO TOP BUTTON
// ===================================
function initBackToTop() {
  const backToTopBtn = document.getElementById("back-to-top");

  if (backToTopBtn) {
    window.addEventListener("scroll", function () {
      if (window.pageYOffset > 300) {
        backToTopBtn.classList.add("show");
      } else {
        backToTopBtn.classList.remove("show");
      }
    });

    backToTopBtn.addEventListener("click", function (e) {
      e.preventDefault();
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    });
  }
}

// ===================================
// AOS (ANIMATE ON SCROLL)
// ===================================
function initAOS() {
  if (typeof AOS !== "undefined") {
    AOS.init({
      duration: 800,
      easing: "ease-in-out",
      once: true,
      offset: 100,
      delay: 100,
    });
  }
}

// ===================================
// SMOOTH SCROLL
// ===================================
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      const href = this.getAttribute("href");
      if (href !== "#" && href !== "#!") {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          const offsetTop = target.offsetTop - 80;
          window.scrollTo({
            top: offsetTop,
            behavior: "smooth",
          });
        }
      }
    });
  });
}

// ===================================
// FORM VALIDATION & SUBMISSION
// ===================================
function initFormValidation() {
  const contactForm = document.getElementById("contact-form");

  if (contactForm) {
    contactForm.addEventListener("submit", async function (e) {
      e.preventDefault();

      // Get form data
      const formData = {
        name: document.getElementById("name").value.trim(),
        email: document.getElementById("email").value.trim(),
        subject: document.getElementById("subject").value.trim(),
        message: document.getElementById("message").value.trim(),
      };

      // Validate
      if (!validateForm(formData)) {
        return;
      }

      // Submit
      await submitContactForm(formData);
    });
  }
}

function validateForm(data) {
  const errors = [];

  // Name validation
  if (data.name.length < 2) {
    errors.push("Name must be at least 2 characters");
  }

  // Email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(data.email)) {
    errors.push("Please enter a valid email address");
  }

  // Subject validation
  if (data.subject.length < 3) {
    errors.push("Subject must be at least 3 characters");
  }

  // Message validation
  if (data.message.length < 10) {
    errors.push("Message must be at least 10 characters");
  }

  // Display errors
  if (errors.length > 0) {
    showNotification(errors.join("<br>"), "error");
    return false;
  }

  return true;
}

async function submitContactForm(data) {
  const submitBtn = document.getElementById("submit-btn");
  const btnText = document.getElementById("btn-text");
  const btnSpinner = document.getElementById("btn-spinner");

  // Show loading state
  submitBtn.disabled = true;
  btnText.classList.add("hidden");
  btnSpinner.classList.remove("hidden");

  try {
    const response = await fetch("/api/contact", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    const result = await response.json();

    if (response.ok && result.success) {
      showNotification(
        "Message sent successfully! I'll get back to you soon.",
        "success"
      );
      document.getElementById("contact-form").reset();
    } else {
      showNotification(
        result.message || "Failed to send message. Please try again.",
        "error"
      );
    }
  } catch (error) {
    console.error("Error:", error);
    showNotification(
      "Network error. Please check your connection and try again.",
      "error"
    );
  } finally {
    // Reset button state
    submitBtn.disabled = false;
    btnText.classList.remove("hidden");
    btnSpinner.classList.add("hidden");
  }
}

// ===================================
// NOTIFICATION SYSTEM
// ===================================
function showNotification(message, type = "info") {
  // Remove existing notification
  const existing = document.getElementById("notification");
  if (existing) {
    existing.remove();
  }

  // Create notification
  const notification = document.createElement("div");
  notification.id = "notification";
  notification.className = `fixed top-20 right-4 max-w-md p-4 rounded-lg shadow-xl z-50 transform transition-all duration-300 ${
    type === "success"
      ? "bg-green-500 text-white"
      : type === "error"
      ? "bg-red-500 text-white"
      : "bg-blue-500 text-white"
  }`;
  notification.innerHTML = `
        <div class="flex items-start">
            <div class="flex-1">
                <p class="font-medium">${message}</p>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;

  document.body.appendChild(notification);

  // Auto remove after 5 seconds
  setTimeout(() => {
    notification.style.opacity = "0";
    notification.style.transform = "translateX(100%)";
    setTimeout(() => notification.remove(), 300);
  }, 5000);
}

// ===================================
// PROJECT FILTERING
// ===================================
function filterProjects(category) {
  const projects = document.querySelectorAll(".project-item");
  const buttons = document.querySelectorAll(".filter-btn");

  // Update active button
  buttons.forEach((btn) => {
    btn.classList.remove("active");
    if (btn.dataset.category === category) {
      btn.classList.add("active");
    }
  });

  // Filter projects
  projects.forEach((project) => {
    if (category === "all" || project.dataset.category === category) {
      project.style.display = "block";
      setTimeout(() => {
        project.style.opacity = "1";
        project.style.transform = "scale(1)";
      }, 10);
    } else {
      project.style.opacity = "0";
      project.style.transform = "scale(0.8)";
      setTimeout(() => {
        project.style.display = "none";
      }, 300);
    }
  });
}

// ===================================
// TYPING EFFECT
// ===================================
function typeWriter(element, text, speed = 100) {
  let i = 0;
  element.innerHTML = "";

  function type() {
    if (i < text.length) {
      element.innerHTML += text.charAt(i);
      i++;
      setTimeout(type, speed);
    }
  }

  type();
}

// ===================================
// UTILITY FUNCTIONS
// ===================================

// Debounce function
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Throttle function
function throttle(func, limit) {
  let inThrottle;
  return function (...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

// Check if element is in viewport
function isInViewport(element) {
  const rect = element.getBoundingClientRect();
  return (
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <=
      (window.innerHeight || document.documentElement.clientHeight) &&
    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
  );
}

// Export functions for use in other scripts
window.portfolioUtils = {
  showNotification,
  filterProjects,
  typeWriter,
  debounce,
  throttle,
  isInViewport,
};
