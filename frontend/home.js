/**
 * ARIA - Homepage JavaScript
 * Authentication and Navigation
 */

// ==================== AUTHENTICATION STATE ====================
const AUTH_KEY = 'aria_user';

// Check if user is logged in on page load
document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initScrollAnimations();
    initSmoothScroll();
});

// ==================== NAVBAR ====================
function initNavbar() {
    const navbar = document.getElementById('navbar');

    // Scroll effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        // Update active nav link based on scroll position
        updateActiveNavLink();
    });
}

function updateActiveNavLink() {
    const sections = ['home', 'features', 'how-it-works', 'about'];
    const navLinks = document.querySelectorAll('.nav-link');

    let currentSection = 'home';

    sections.forEach(sectionId => {
        const section = document.getElementById(sectionId);
        if (section) {
            const rect = section.getBoundingClientRect();
            if (rect.top <= 200 && rect.bottom >= 200) {
                currentSection = sectionId;
            }
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${currentSection}`) {
            link.classList.add('active');
        }
    });
}

function toggleNav() {
    const navLinks = document.querySelector('.nav-links');
    const navButtons = document.querySelector('.nav-buttons');
    navLinks.classList.toggle('active');
    navButtons.classList.toggle('active');
}

// ==================== SCROLL ANIMATIONS ====================
function initScrollAnimations() {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements
    document.querySelectorAll('.feature-card, .step, .cta-content').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
        observer.observe(el);
    });
}

// Add CSS for animated elements
const style = document.createElement('style');
style.textContent = `
    .animate-in {
        opacity: 1 !important;
        transform: translateY(0) !important;
    }
`;
document.head.appendChild(style);

// ==================== SMOOTH SCROLL ====================
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            scrollToSection(targetId.substring(1));
        });
    });
}

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        const offset = 100; // Account for fixed navbar
        const top = section.offsetTop - offset;
        window.scrollTo({
            top: top,
            behavior: 'smooth'
        });
    }
}

// ==================== MODALS ====================
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    // Focus first input
    setTimeout(() => {
        const firstInput = modal.querySelector('input');
        if (firstInput) firstInput.focus();
    }, 300);
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('active');
    document.body.style.overflow = '';
}

function switchModal(fromId, toId) {
    closeModal(fromId);
    setTimeout(() => openModal(toId), 200);
}

// Close modal on overlay click
document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
});

// Close modal on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.active').forEach(modal => {
            modal.classList.remove('active');
        });
        document.body.style.overflow = '';
    }
});

// ==================== AUTHENTICATION ====================
function handleLogin(event) {
    event.preventDefault();

    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    // Validate
    if (!email || !password) {
        showToast('Please fill in all fields', 'error');
        return;
    }

    // Show loading
    const btn = event.target.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="loading"></span> Signing in...';
    btn.disabled = true;

    // Simulate API call (replace with real API in production)
    setTimeout(() => {
        // Check if user exists in localStorage
        const users = JSON.parse(localStorage.getItem('aria_users') || '[]');
        const user = users.find(u => u.email === email);

        if (user && user.password === password) {
            // Login successful
            const userData = {
                name: user.name,
                email: user.email,
                loggedIn: true,
                loginTime: new Date().toISOString()
            };

            localStorage.setItem(AUTH_KEY, JSON.stringify(userData));

            showToast('Welcome back! Redirecting...', 'success');

            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);
        } else {
            // Login failed - for demo, create user and login
            showToast('Invalid credentials. Try signing up!', 'error');
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    }, 1500);
}

function handleSignup(event) {
    event.preventDefault();

    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const confirm = document.getElementById('signupConfirm').value;

    // Validate
    if (!name || !email || !password || !confirm) {
        showToast('Please fill in all fields', 'error');
        return;
    }

    if (password !== confirm) {
        showToast('Passwords do not match', 'error');
        return;
    }

    if (password.length < 6) {
        showToast('Password must be at least 6 characters', 'error');
        return;
    }

    // Show loading
    const btn = event.target.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="loading"></span> Creating account...';
    btn.disabled = true;

    // Simulate API call
    setTimeout(() => {
        // Save user to localStorage
        const users = JSON.parse(localStorage.getItem('aria_users') || '[]');

        // Check if email already exists
        if (users.find(u => u.email === email)) {
            showToast('Email already registered. Please sign in.', 'error');
            btn.innerHTML = originalText;
            btn.disabled = false;
            return;
        }

        // Create new user
        const newUser = {
            id: Date.now(),
            name: name,
            email: email,
            password: password, // In production, hash this!
            createdAt: new Date().toISOString()
        };

        users.push(newUser);
        localStorage.setItem('aria_users', JSON.stringify(users));

        // Auto login
        const userData = {
            name: name,
            email: email,
            loggedIn: true,
            loginTime: new Date().toISOString()
        };

        localStorage.setItem(AUTH_KEY, JSON.stringify(userData));

        showToast('Account created! Redirecting...', 'success');

        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1000);
    }, 1500);
}

// ==================== AUTH HELPERS ====================
function isLoggedIn() {
    const user = localStorage.getItem(AUTH_KEY);
    if (user) {
        const userData = JSON.parse(user);
        return userData.loggedIn === true;
    }
    return false;
}

function getCurrentUser() {
    const user = localStorage.getItem(AUTH_KEY);
    return user ? JSON.parse(user) : null;
}

function logout() {
    localStorage.removeItem(AUTH_KEY);
    window.location.href = 'index.html';
}

// ==================== GOOGLE OAUTH ====================
async function loginWithGoogle() {
    try {
        const apiUrl = window.location.hostname === 'localhost'
            ? 'http://localhost:5000/auth/google'
            : 'https://disciplined-embrace-production-9079.up.railway.app/auth/google';
        const response = await fetch(apiUrl);
        const data = await response.json();

        if (data.authorization_url) {
            // Redirect to Google OAuth
            window.location.href = data.authorization_url;
        } else {
            showToast('Google Sign-In error. Please check backend setup.', 'error');
        }
    } catch (error) {
        console.error('Google OAuth error:', error);
        showToast('Unable to connect to authentication server', 'error');
    }
}

// Check for OAuth callback parameters on page load
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);

    if (urlParams.has('oauth_success')) {
        const email = urlParams.get('email');

        // Create user session
        const userData = {
            name: urlParams.get('name') || email.split('@')[0],
            email: email,
            loggedIn: true,
            googleAuth: true,
            loginTime: new Date().toISOString()
        };

        localStorage.setItem(AUTH_KEY, JSON.stringify(userData));

        showToast('Google Sign-In successful! Redirecting...', 'success');

        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1000);
    } else if (urlParams.has('oauth_error')) {
        showToast('Google Sign-In failed. Please try again.', 'error');
        // Clean up URL
        window.history.replaceState({}, '', '/');
    }
});

// ==================== GLOBAL FUNCTIONS ====================
window.openModal = openModal;
window.closeModal = closeModal;
window.switchModal = switchModal;
window.handleLogin = handleLogin;
window.handleSignup = handleSignup;
window.loginWithGoogle = loginWithGoogle;
window.scrollToSection = scrollToSection;
window.toggleNav = toggleNav;
window.logout = logout;

// ==================== TOAST NOTIFICATIONS ====================
function showToast(message, type = 'info') {
    // Remove existing toasts
    document.querySelectorAll('.toast-notification').forEach(t => t.remove());

    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        border-radius: 12px;
        background: ${type === 'success' ? 'linear-gradient(135deg, #10b981, #059669)' :
            type === 'error' ? 'linear-gradient(135deg, #ef4444, #dc2626)' :
                'linear-gradient(135deg, #7c3aed, #6d28d9)'};
        color: white;
        font-weight: 500;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    toast.textContent = message;

    // Add animation styles
    if (!document.getElementById('toast-styles')) {
        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }

    document.body.appendChild(toast);

    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Console branding
console.log('%c🚀 ARIA', 'font-size: 24px; font-weight: bold; color: #7c3aed;');
console.log('%cAI-Powered Personal Task Automation', 'font-size: 12px; color: #a855f7;');
