document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("evidence-modal");
    const openBtn = document.getElementById("open-evidence");
    const closeBtn = document.querySelector(".close-btn");
    const rulesBtn = document.getElementById("rules-btn");
  
    // Open evidence modal
    openBtn?.addEventListener("click", () => {
      modal.classList.remove("hidden");
    });
  
    // Close evidence modal
    closeBtn?.addEventListener("click", () => {
      modal.classList.add("hidden");
    });
  
    // Toggle rules box
    rulesBtn?.addEventListener("click", () => {
      location.href = "/rules";
    });
  });