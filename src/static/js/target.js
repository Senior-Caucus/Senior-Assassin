document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("evidence-modal");
    const openBtn = document.getElementById("open-evidence");
    const closeBtn = document.querySelector(".close-btn");
    const rulesBtn = document.getElementById("rules-btn");
    const rulesBox = document.getElementById("rules-box");
  
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
      rulesBox.classList.toggle("hidden");
    });
  });