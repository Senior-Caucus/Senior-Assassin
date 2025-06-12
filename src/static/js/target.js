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

  // --- new game mode logic ---
  const userSelect = document.getElementById("user-select");
  const userInfoDiv = document.getElementById("user-info");
  const submitBtn = document.getElementById("submit-evidence-btn");
  const targetEmailInput = document.getElementById("target_email");

  function renderUserInfo(email) {
    const user = window.ALL_USERS.find((u) => u.email === email);
    if (!user) return;
    userInfoDiv.innerHTML = `
      <h3>${user.fullName} (${user.hearts || 0}❤)</h3>
      <img src="${user.picture}" alt="Profile Picture" style="max-width:120px;max-height:120px;border-radius:8px;" onerror="this.style.display='none'">
      <p><b>Height:</b> ${user.feet || ''}'${user.inches || ''}"</p>
      <table><thead><tr><th>Period</th><th>Class</th></tr></thead><tbody>
        ${(user.schedule||'').split(',').map((c,i)=>`<tr><td>${i+1}</td><td>${c||'None'}</td></tr>`).join('')}
      </tbody></table>
    `;
    targetEmailInput.value = user.email;
  }

  function checkEvidenceDisabled(targetEmail) {
    const already = window.EVIDENCE.some(
      (e) => e.assassin === window.CURRENT_USER_EMAIL && e.target === targetEmail
    );
    submitBtn.disabled = already;
    submitBtn.textContent = already ? "Already Submitted" : "Submit";
    return already;
  }

  userSelect.addEventListener("change", (e) => {
    const email = e.target.value;
    renderUserInfo(email);
    checkEvidenceDisabled(email);
  });

  // Initial render
  if (userSelect.value) {
    renderUserInfo(userSelect.value);
    checkEvidenceDisabled(userSelect.value);
  }
  // When opening modal, set target_email
  openBtn?.addEventListener("click", () => {
    targetEmailInput.value = userSelect.value;
    checkEvidenceDisabled(userSelect.value);
    modal.classList.remove("hidden");
  });
});