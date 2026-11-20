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
    const img = el.querySelector('img');
    const lightboxImg = document.getElementById('lightbox-img');
    const fallback = document.getElementById('lightbox-fallback');

    // Real screenshot: show the image, hide the placeholder
    if (img && lightboxImg) {
        lightboxImg.src = img.src;
        lightboxImg.classList.add('visible');
        if (fallback) fallback.style.display = 'none';
        document.getElementById('lightbox-title').textContent = el.dataset.title || 'Screenshot';
        document.getElementById('lightbox-desc').textContent = el.dataset.desc || '';
    } else {
        // Legacy placeholder
        const span = el.querySelector('span');
        const small = el.querySelector('small');
        if (span) document.getElementById('lightbox-title').textContent = span.textContent;
        if (small) document.getElementById('lightbox-desc').textContent = small.textContent;
        if (lightboxImg) lightboxImg.classList.remove('visible');
        if (fallback) fallback.style.display = '';
    }

    document.getElementById('lightbox').classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeLightbox() {
    document.getElementById('lightbox').classList.remove('active');
    const lightboxImg = document.getElementById('lightbox-img');
    if (lightboxImg) lightboxImg.classList.remove('visible');
    const fallback = document.getElementById('lightbox-fallback');
    if (fallback) fallback.style.display = '';
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