document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("review-modal");
    const closeBtn = document.querySelector(".close-btn");
    const videoElement = document.getElementById("evidence-video");
  
    // Open modal
    document.querySelectorAll(".review-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const videoSrc = btn.getAttribute("data-video");
        videoElement.src = videoSrc;
        modal.classList.remove("hidden");
      });
    });
  
    // Close modal
    closeBtn?.addEventListener("click", () => {
      modal.classList.add("hidden");
      videoElement.pause();
      videoElement.currentTime = 0;
      videoElement.src = "";
    });
  });