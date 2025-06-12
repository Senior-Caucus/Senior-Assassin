document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("evidence-modal");
  const openBtn = document.getElementById("open-evidence");
  const closeBtn = document.querySelector(".close-btn");
  const rulesBtn = document.getElementById("rules-btn");

  // --- modal controls ---
  openBtn?.addEventListener("click", () => modal.classList.remove("hidden"));
  closeBtn?.addEventListener("click", closeModal);
  rulesBtn?.addEventListener("click", () => (location.href = "/rules"));

  function closeModal() {
    modal.classList.add("hidden");
    // form.reset();
    // progressContainer.classList.add("hidden");
    // progressBar.style.width = "0";
    // uploadMsg.textContent = "";
  }

  // --- new game mode logic ---
  const userSelect = document.getElementById("user-select");
  const userInfoDiv = document.getElementById("user-info");
  const submitBtn = document.getElementById("submit-evidence-btn");
  const targetEmailInput = document.getElementById("target_email");
  const showUserInfoBtn = document.getElementById("show-user-info");

  function renderUserInfo(email) {
    const user = ALL_USERS.find((u) => u.email === email);
    if (!user) return;
    // Find all evidence for this user
    const evidenceList = EVIDENCE.filter(e => e.target === email);
    let evidenceHtml = "";
    if (evidenceList.length > 0) {
      evidenceHtml = `<div style='margin-top:1em;'><b>Evidence submitted for this user:</b><ul>` +
        evidenceList.map(function(e) {
          return `<li>By: ${e.assassin}${e.comments ? ' (Comment: ' + e.comments + ')' : ''}</li>`;
        }).join('') +
        `</ul></div>`;
    } else {
      evidenceHtml = `<div style='margin-top:1em;'><i>No evidence submitted for this user yet.</i></div>`;
    }
    // Responsive image size
    let imgSize = 160;
    if (window.innerWidth > 900) imgSize = 220;
    else if (window.innerWidth > 600) imgSize = 180;
    // Loading spinner
    // Evidence submit form (always rendered in user info)
    let already = EVIDENCE.some(e => e.assassin === CURRENT_USER_EMAIL && e.target === user.email);
    let submitForm = `
      <form id="evidence-form" method="post" enctype="multipart/form-data" style="margin-top:1.5em;">
        <label for="video">Video Evidence (max 25MB):</label>
        <input type="file" name="video" id="video" accept="video/*" required><br>
        <label for="comments">Comments:</label>
        <textarea name="comments" id="comments" rows="3" placeholder="Optional..."></textarea>
        <input type="hidden" name="target_email" id="target_email" value="${user.email}">
        <input type="hidden" name="user_email" value="${CURRENT_USER_EMAIL}">
        <div id="progress-container" class="hidden"><div id="upload-progress"></div></div>
        <p id="upload-msg" class="upload-msg"></p>
        <button type="submit" class="submit-btn" id="submit-evidence-btn" ${already ? 'disabled' : ''}>${already ? 'Already Submitted' : 'Submit Evidence'}</button>
      </form>
    `;
    userInfoDiv.innerHTML = `
      <h3>${user.fullName} (${user.hearts || 0}❤)</h3>
      <p><b>Height:</b> ${user.feet || ''}'${user.inches || ''}"</p>
      <table><thead><tr><th>Period</th><th>Class</th></tr></thead><tbody>
        ${(user.schedule||'').split(',').map(function(c,i){return `<tr><td>${i+1}</td><td>${c||'None'}</td></tr>`;}).join('')}
      </tbody></table>
      <div style="position:relative;min-height:${imgSize}px;">
        <div id="img-loading-spinner" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);font-size:2em;">⏳</div>
        <img id="profile-pic" src="${user.picture}" alt="Profile Picture" style="display:none;max-width:${imgSize}px;max-height:${imgSize}px;border-radius:8px;" onerror="this.style.display='none'">
      </div>
      ${evidenceHtml}
      ${submitForm}
    `;
    // Image loading logic
    const img = document.getElementById('profile-pic');
    const spinner = document.getElementById('img-loading-spinner');
    if (img) {
      img.onload = function() {
        img.style.display = 'block';
        if (spinner) spinner.style.display = 'none';
      };
      img.onerror = function() {
        if (spinner) spinner.style.display = 'none';
      };
    }
    // Attach submit logic to the new form
    const form = document.getElementById("evidence-form");
    const fileInput = document.getElementById("video");
    const progressContainer = document.getElementById("progress-container");
    const progressBar = document.getElementById("upload-progress");
    const uploadMsg = document.getElementById("upload-msg");
    if (form) {
      form.addEventListener("submit", function(e) {
        e.preventDefault();
        uploadMsg.textContent = "";
        const file = fileInput.files[0];
        if (!file) {
          uploadMsg.textContent = "Please select a file.";
          uploadMsg.style.color = "red";
          return;
        }
        const MAX = 25 * 1024 * 1024;
        if (file.size > MAX) {
          uploadMsg.textContent = "File too large (max 25 MB).";
          uploadMsg.style.color = "red";
          return;
        }
        const formData = new FormData(form);
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/user/submit-evidence", true);
        progressContainer.classList.remove("hidden");
        progressBar.style.width = "0%";
        xhr.upload.addEventListener("progress", function(evt) {
          if (evt.lengthComputable) {
            const pct = Math.round((evt.loaded / evt.total) * 100);
            progressBar.style.width = pct + "%";
            uploadMsg.textContent = pct + "% uploaded…";
            uploadMsg.style.color = "#FFF";
          }
        });
        xhr.onload = function() {
          if (xhr.status === 200) {
            progressBar.style.width = "100%";
            uploadMsg.textContent = "Upload complete!";
            uploadMsg.style.color = "green";
            setTimeout(function() {
              progressContainer.classList.add("hidden");
              progressBar.style.width = "0%";
              uploadMsg.textContent = "";
              form.reset();
              // Refresh page to update evidence and hearts
              window.location.reload();
            }, 500);
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
        xhr.onerror = function() {
          uploadMsg.textContent = "Network error.";
          uploadMsg.style.color = "red";
        };
        xhr.send(formData);
      });
    }
    checkEvidenceDisabled(user.email);
  }

  function checkEvidenceDisabled(targetEmail) {
    const already = EVIDENCE.some(
      (e) => e.assassin === CURRENT_USER_EMAIL && e.target === targetEmail
    );
    submitBtn.disabled = already;
    submitBtn.textContent = already ? "Already Submitted" : "Submit";
    return already;
  }

  showUserInfoBtn.addEventListener("click", function() {
    renderUserInfo(userSelect.value);
  });

  // Remove auto-render on select change
  // When opening modal, set target_email
  openBtn?.addEventListener("click", function() {
    targetEmailInput.value = userSelect.value;
    checkEvidenceDisabled(userSelect.value);
    modal.classList.remove("hidden");
  });
});