// ── TOAST ─────────────────────────────────────────────────
function showToast(msg, duration = 3000) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), duration);
}

// ── MODAL ─────────────────────────────────────────────────
function closeModal() {
  document.getElementById('modal-overlay').classList.add('hidden');
  document.getElementById('modal-content').innerHTML = '';
}

document.getElementById('modal-overlay').addEventListener('click', function(e) {
  if (e.target === this) closeModal();
});

// ── PREVENT DOUBLE TAP ZOOM on buttons ───────────────────
document.addEventListener('touchend', function(e) {
  if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A') {
    e.preventDefault();
    e.target.click();
  }
}, { passive: false });

// ── MARK ACTIVE NAV ───────────────────────────────────────
document.querySelectorAll('.nav-link').forEach(link => {
  if (link.getAttribute('href') === window.location.pathname) {
    link.classList.add('active');
  } else {
    link.classList.remove('active');
  }
});
