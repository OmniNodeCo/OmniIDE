/* OmniIDE Website Scripts */

// ── Mobile nav toggle ──
function toggleMenu() {
    document.querySelector('.nav-links').classList.toggle('open');
}

// Close menu on link click
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => {
        document.querySelector('.nav-links').classList.remove('open');
    });
});

// ── Navbar scroll effect ──
window.addEventListener('scroll', () => {
    const nav = document.getElementById('navbar');
    if (window.scrollY > 50) {
        nav.style.background = 'rgba(24, 24, 37, 0.95)';
    } else {
        nav.style.background = 'rgba(24, 24, 37, 0.85)';
    }
});

// ── FAQ toggle ──
function toggleFaq(btn) {
    const item = btn.parentElement;
    const wasOpen = item.classList.contains('open');

    // Close all
    document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));

    // Open clicked (if it wasn't already open)
    if (!wasOpen) {
        item.classList.add('open');
    }
}

// ── Lightbox ──
function openLightbox(el) {
    const title = el.querySelector('span').textContent;
    const desc = el.querySelector('small').textContent;

    document.getElementById('lightbox-title').textContent = title;
    document.getElementById('lightbox-desc').textContent = desc;
    document.getElementById('lightbox').classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeLightbox() {
    document.getElementById('lightbox').classList.remove('active');
    document.body.style.overflow = '';
}

// Close on Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeLightbox();
    }
});

// ── Detect platform and highlight download card ──
function detectPlatform() {
    const ua = navigator.userAgent.toLowerCase();
    let platform = null;

    if (ua.includes('win')) {
        platform = 'dl-windows';
    } else if (ua.includes('mac') || ua.includes('darwin')) {
        platform = 'dl-macos';
    } else if (ua.includes('linux') || ua.includes('x11')) {
        platform = 'dl-linux';
    }

    if (platform) {
        const card = document.getElementById(platform);
        if (card) {
            card.classList.add('current-platform');
        }
    }
}

// ── Smooth scroll for anchor links ──
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// ── Init ──
document.addEventListener('DOMContentLoaded', () => {
    detectPlatform();
});