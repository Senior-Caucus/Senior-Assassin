document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("evidence-modal");
  const openBtn = document.getElementById("open-evidence");
  const closeBtn = document.querySelector(".close-btn");
  const rulesBtn = document.getElementById("rules-btn");

  const form = document.getElementById("evidence-form");
  const videoInput = document.getElementById("video");
  const progressContainer = document.getElementById("progress-container");
  const progressBar = document.getElementById("upload-progress");
  const uploadMsg = document.getElementById("upload-msg");

  // --- modal controls ---
  openBtn?.addEventListener("click", () => modal.classList.remove("hidden"));
  closeBtn?.addEventListener("click", closeModal);
  rulesBtn?.addEventListener("click", () => (location.href = "/rules"));

  function closeModal() {
    modal.classList.add("hidden");
    form.reset();
    progressContainer.classList.add("hidden");
    progressBar.style.width = "0";
    uploadMsg.textContent = "";
  }

  // --- form submit with progress ---
  form?.addEventListener("submit", (e) => {
    e.preventDefault();

    const file = videoInput.files[0];
    if (!file) return;

    // 25 MB size limit
    const maxBytes = 25 * 1024 * 1024;
    if (file.size > maxBytes) {
      uploadMsg.textContent = "File too large (max 25 MB).";
      uploadMsg.style.color = "red";
      return;
    }

    const formData = new FormData(form);
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/user/submit-evidence", true);

    // progress
    progressContainer.classList.remove("hidden");
    xhr.upload.onprogress = (evt) => {
      if (evt.lengthComputable) {
        const pct = (evt.loaded / evt.total) * 100;
        progressBar.style.width = pct + "%";
      }
    };

    xhr.onload = () => {
      if (xhr.status === 200) {
        uploadMsg.textContent = "Upload complete!";
        uploadMsg.style.color = "lime";
        setTimeout(closeModal, 1500);
      } else {
        uploadMsg.textContent = "Error uploading evidence.";
        uploadMsg.style.color = "red";
      }
    };

    xhr.onerror = () => {
      uploadMsg.textContent = "Network error.";
      uploadMsg.style.color = "red";
    };

    xhr.send(formData);
  });
});