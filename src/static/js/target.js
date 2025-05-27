document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("evidence-modal");
  const openBtn = document.getElementById("open-evidence");
  const closeBtn = document.querySelector(".close-btn");
  const rulesBtn = document.getElementById("rules-btn");

  const form = document.getElementById("evidence-form");
  const fileInput = document.getElementById("video");
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

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    uploadMsg.textContent = "";

    const file = fileInput.files[0];
    if (!file) {
      uploadMsg.textContent = "Please select a file.";
      uploadMsg.style.color = "red";
      return;
    }

    const MAX = 25 * 1024 * 1024; // 25 MB
    if (file.size > MAX) {
      uploadMsg.textContent = "File too large (max 25 MB).";
      uploadMsg.style.color = "red";
      return;
    }

    const formData = new FormData(form);
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/user/submit-evidence", true);

    // show the bar
    progressContainer.style.display = "block";

    xhr.upload.addEventListener("progress", (evt) => {
      if (evt.lengthComputable) {
        const pct = Math.round((evt.loaded / evt.total) * 100);
        progressBar.style.width = pct + "%";
        uploadMsg.textContent = pct + "% uploaded…";
        uploadMsg.style.color = "#FFF";
      }
    });

    xhr.onload = () => {
      if (xhr.status === 200) {
        progressBar.style.width = "100%";
        uploadMsg.textContent = "Upload complete!";
        uploadMsg.style.color = "green";
        setTimeout(() => {
          // reset UI
          progressContainer.style.display = "none";
          progressBar.style.width = "0%";
          uploadMsg.textContent = "";
          form.reset();
          document.getElementById("evidence-modal").classList.add("hidden");
        }, 250);
        const res = JSON.parse(xhr.responseText);
        if (res.redirect) {
          window.location.href = res.redirect;
          return;
        }
      } else {
        uploadMsg.textContent = "Error: " + xhr.responseText;
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