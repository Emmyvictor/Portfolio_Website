// ===================================
// ANIMATIONS - PORTFOLIO
// ===================================

document.addEventListener("DOMContentLoaded", function () {
  initFadeInAnimations();
  initSkillBars();
  initCounterAnimations();
  initParallaxEffect();
  initCursorEffect();
});

// ===================================
// FADE IN ANIMATIONS
// ===================================
function initFadeInAnimations() {
  const fadeElements = document.querySelectorAll(".fade-in-up");

  if (fadeElements.length === 0) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
        }
      });
    },
    {
      threshold: 0.1,
      rootMargin: "0px 0px -50px 0px",
    }
  );

  fadeElements.forEach((element) => {
    observer.observe(element);
  });
}

// ===================================
// SKILL BAR ANIMATIONS
// ===================================
function initSkillBars() {
  const skillBars = document.querySelectorAll(".skill-progress");

  if (skillBars.length === 0) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const progress = entry.target;
          const width = progress.dataset.width || "0%";

          setTimeout(() => {
            progress.style.width = width;
          }, 200);

          observer.unobserve(entry.target);
        }
      });
    },
    {
      threshold: 0.5,
    }
  );

  skillBars.forEach((bar) => {
    bar.style.width = "0%";
    observer.observe(bar);
  });
}

// ===================================
// COUNTER ANIMATIONS
// ===================================
function initCounterAnimations() {
  const counters = document.querySelectorAll(".counter");

  if (counters.length === 0) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          observer.unobserve(entry.target);
        }
      });
    },
    {
      threshold: 0.5,
    }
  );

  counters.forEach((counter) => {
    observer.observe(counter);
  });
}

function animateCounter(element) {
  const target = parseInt(element.dataset.target) || 0;
  const duration = parseInt(element.dataset.duration) || 2000;
  const increment = target / (duration / 16);
  let current = 0;

  const timer = setInterval(() => {
    current += increment;
    if (current >= target) {
      element.textContent = target;
      clearInterval(timer);
    } else {
      element.textContent = Math.floor(current);
    }
  }, 16);
}

// ===================================
// PARALLAX EFFECT
// ===================================
function initParallaxEffect() {
  const parallaxElements = document.querySelectorAll(".parallax");

  if (parallaxElements.length === 0) return;

  window.addEventListener("scroll", throttleParallax);
}

const throttleParallax = throttle(function () {
  const parallaxElements = document.querySelectorAll(".parallax");
  const scrolled = window.pageYOffset;

  parallaxElements.forEach((element) => {
    const speed = element.dataset.speed || 0.5;
    const yPos = -(scrolled * speed);
    element.style.transform = `translateY(${yPos}px)`;
  });
}, 10);

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

// ===================================
// CUSTOM CURSOR EFFECT (OPTIONAL)
// ===================================
function initCursorEffect() {
  const cursor = document.createElement("div");
  cursor.className = "custom-cursor";
  cursor.style.cssText = `
        position: fixed;
        width: 20px;
        height: 20px;
        border: 2px solid #000;
        border-radius: 50%;
        pointer-events: none;
        z-index: 9999;
        transition: transform 0.15s ease;
        display: none;
    `;

  const cursorFollower = document.createElement("div");
  cursorFollower.className = "cursor-follower";
  cursorFollower.style.cssText = `
        position: fixed;
        width: 40px;
        height: 40px;
        border: 1px solid rgba(0, 0, 0, 0.3);
        border-radius: 50%;
        pointer-events: none;
        z-index: 9998;
        transition: transform 0.3s ease;
        display: none;
    `;

  // Only show on desktop
  if (window.innerWidth > 768) {
    document.body.appendChild(cursor);
    document.body.appendChild(cursorFollower);
    cursor.style.display = "block";
    cursorFollower.style.display = "block";

    let mouseX = 0,
      mouseY = 0;
    let followerX = 0,
      followerY = 0;

    document.addEventListener("mousemove", (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;

      cursor.style.left = mouseX - 10 + "px";
      cursor.style.top = mouseY - 10 + "px";
    });

    // Smooth follower animation
    function animateFollower() {
      followerX += (mouseX - followerX) * 0.1;
      followerY += (mouseY - followerY) * 0.1;

      cursorFollower.style.left = followerX - 20 + "px";
      cursorFollower.style.top = followerY - 20 + "px";

      requestAnimationFrame(animateFollower);
    }
    animateFollower();

    // Hover effects
    const hoverElements = document.querySelectorAll(
      "a, button, .project-card, .card"
    );
    hoverElements.forEach((element) => {
      element.addEventListener("mouseenter", () => {
        cursor.style.transform = "scale(1.5)";
        cursorFollower.style.transform = "scale(1.5)";
      });

      element.addEventListener("mouseleave", () => {
        cursor.style.transform = "scale(1)";
        cursorFollower.style.transform = "scale(1)";
      });
    });
  }
}

// ===================================
// TYPING ANIMATION
// ===================================
function initTypingAnimation(
  elementId,
  texts,
  speed = 100,
  deleteSpeed = 50,
  pauseTime = 2000
) {
  const element = document.getElementById(elementId);
  if (!element) return;

  let textIndex = 0;
  let charIndex = 0;
  let isDeleting = false;

  function type() {
    const currentText = texts[textIndex];

    if (isDeleting) {
      element.textContent = currentText.substring(0, charIndex - 1);
      charIndex--;
    } else {
      element.textContent = currentText.substring(0, charIndex + 1);
      charIndex++;
    }

    let typeSpeed = isDeleting ? deleteSpeed : speed;

    if (!isDeleting && charIndex === currentText.length) {
      typeSpeed = pauseTime;
      isDeleting = true;
    } else if (isDeleting && charIndex === 0) {
      isDeleting = false;
      textIndex = (textIndex + 1) % texts.length;
      typeSpeed = 500;
    }

    setTimeout(type, typeSpeed);
  }

  type();
}

// ===================================
// STAGGER ANIMATION
// ===================================
function staggerAnimation(selector, delay = 100) {
  const elements = document.querySelectorAll(selector);

  elements.forEach((element, index) => {
    element.style.opacity = "0";
    element.style.transform = "translateY(20px)";

    setTimeout(() => {
      element.style.transition = "all 0.5s ease";
      element.style.opacity = "1";
      element.style.transform = "translateY(0)";
    }, index * delay);
  });
}

// ===================================
// REVEAL ON SCROLL
// ===================================
function revealOnScroll() {
  const reveals = document.querySelectorAll(".reveal");

  reveals.forEach((element) => {
    const windowHeight = window.innerHeight;
    const elementTop = element.getBoundingClientRect().top;
    const elementVisible = 150;

    if (elementTop < windowHeight - elementVisible) {
      element.classList.add("active");
    }
  });
}

window.addEventListener("scroll", revealOnScroll);

// ===================================
// IMAGE LAZY LOADING
// ===================================
function initLazyLoading() {
  const images = document.querySelectorAll("img[data-src]");

  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.removeAttribute("data-src");
        imageObserver.unobserve(img);

        img.addEventListener("load", () => {
          img.style.opacity = "1";
        });
      }
    });
  });

  images.forEach((img) => {
    img.style.opacity = "0";
    img.style.transition = "opacity 0.3s ease";
    imageObserver.observe(img);
  });
}

// Initialize lazy loading
initLazyLoading();

// ===================================
// SMOOTH SCROLL TO SECTION
// ===================================
function smoothScrollTo(targetId, duration = 1000) {
  const target = document.getElementById(targetId);
  if (!target) return;

  const targetPosition = target.offsetTop - 80;
  const startPosition = window.pageYOffset;
  const distance = targetPosition - startPosition;
  let startTime = null;

  function animation(currentTime) {
    if (startTime === null) startTime = currentTime;
    const timeElapsed = currentTime - startTime;
    const run = easeInOutQuad(timeElapsed, startPosition, distance, duration);
    window.scrollTo(0, run);
    if (timeElapsed < duration) requestAnimationFrame(animation);
  }

  function easeInOutQuad(t, b, c, d) {
    t /= d / 2;
    if (t < 1) return (c / 2) * t * t + b;
    t--;
    return (-c / 2) * (t * (t - 2) - 1) + b;
  }

  requestAnimationFrame(animation);
}

// ===================================
// EXPORT FUNCTIONS
// ===================================
window.portfolioAnimations = {
  initTypingAnimation,
  staggerAnimation,
  smoothScrollTo,
  animateCounter,
};
