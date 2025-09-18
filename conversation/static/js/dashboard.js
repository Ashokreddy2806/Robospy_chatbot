// ====DOM ELEMENTS ====
const dashboard = document.getElementById("dashboard");

// ==== DASHBOARD ANIMATION ====
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('.green-bar').forEach(bar => {
    const finalWidth = bar.dataset.width;
    setTimeout(() => { bar.style.width = finalWidth + '%'; }, 100);
  });
});
