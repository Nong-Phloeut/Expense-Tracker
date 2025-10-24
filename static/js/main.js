// main.js - small JS helpers
document.addEventListener("DOMContentLoaded", function () {
  // Example: auto-dismiss alerts with data-auto-dismiss
  document.querySelectorAll("[data-auto-dismiss]").forEach(function (el) {
    const seconds = parseInt(el.dataset.autoDismiss, 10) || 5;
    setTimeout(() => el.remove(), seconds * 1000);
  });
});
