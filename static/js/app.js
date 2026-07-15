/**
 * app.js – Shared JS for WanderAI
 * Handles the loading overlay on form submission.
 */
(function () {
  "use strict";

  const form    = document.getElementById("planForm");
  const overlay = document.getElementById("loadingOverlay");
  const btn     = document.getElementById("submitBtn");

  if (form && overlay) {
    form.addEventListener("submit", function (e) {
      // Basic client-side check: at least one interest checked
      const checked = form.querySelectorAll('input[name="interests"]:checked');
      if (checked.length === 0) {
        // Check the first one silently so the form still submits with a default
        const first = form.querySelector('input[name="interests"]');
        if (first) first.checked = true;
      }

      overlay.classList.remove("d-none");
      overlay.style.display = "flex";
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating…';
      }
    });
  }
})();
