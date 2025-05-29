document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("review-modal");
  const closeBtn = document.querySelector(".close-btn");
  const videoEl = document.getElementById("evidence-video");
  const approveBtn = document.querySelector(".approve-btn");
  const denyBtn    = document.querySelector(".deny-btn");
  const assassinImg  = modal.querySelector("#assassin-pic");
  const targetImg    = modal.querySelector("#target-pic");

  let currentId = null;

  // Open modal
    document.querySelectorAll(".review-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      currentId = btn.dataset.id;
      videoEl.src = btn.dataset.videoUrl;
      videoEl.load();
      modal.classList.remove("hidden");
      // Add the url for the profile pictures
      //assassinImg.src   = btn.dataset.assassinUrl;
      //targetImg.src     = btn.dataset.targetUrl;
      //console.log(Assassin URL: ${btn.dataset.assassinUrl});
      //console.log(Target URL: ${btn.dataset.targetUrl});
    });
  });

  // Close helper
  function closeModal() {
    modal.classList.add("hidden");
    videoEl.pause();
    videoEl.currentTime = 0;
    videoEl.src = "";
    currentId = null;
  }

  closeBtn.addEventListener("click", closeModal);

  // Approve / Deny handler
  function sendDecision(approved) {
    if (!currentId) return;
    fetch(`/admin/approve-evidence/${currentId}/${approved}`, {
      method: "POST"
    })
    .then(res => {
      if (!res.ok) throw new Error("Failed to update");
      // remove row from table
      const row = document.getElementById(`row-${currentId}`);
      row?.parentNode.removeChild(row);
      closeModal();
    })
    .catch(err => {
      alert("Error: " + err.message);
    });
  }

  approveBtn.addEventListener("click", () => sendDecision(true));
  denyBtn   .addEventListener("click", () => sendDecision(false));
});