/**
 * 3D Print Manager — app.js
 * - Auto-dismiss flash alerts after 5 seconds
 * - HTMX afterSwap: close dialog after form submit inside a dialog
 */

(function () {
  "use strict";

  // ── Auto-dismiss flash message ──────────────────────────────────────────
  function autoDismissFlash() {
    const el = document.getElementById("flash-msg");
    if (!el) return;
    setTimeout(() => {
      el.style.transition = "opacity .4s ease";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 400);
    }, 5000);
  }

  // ── HTMX: after any swap, remove empty rows (HTMX delete returns "")
  document.addEventListener("htmx:afterSwap", function (evt) {
    const target = evt.detail.target;
    if (target && target.innerHTML.trim() === "") {
      target.remove();
    }
  });

  document.addEventListener("DOMContentLoaded", function () {
    autoDismissFlash();
  });
})();
