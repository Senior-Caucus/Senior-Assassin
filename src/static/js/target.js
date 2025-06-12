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

  // Utility: render hearts as images
  function renderHearts(container, hearts) {
    container.innerHTML = '';
    let n = parseFloat(hearts || '0');
    let imgs = [];
    while (n >= 1) {
      imgs.push(`<img src="/static/images/hearts/oneheart.png" alt="1 heart" style="width:28px;height:28px;vertical-align:middle;">`);
      n -= 1;
    }
    if (Math.abs(n - 2/3) < 0.01) {
      imgs.push(`<img src="/static/images/hearts/twothirdheart.png" alt="2/3 heart" style="width:28px;height:28px;vertical-align:middle;">`);
    } else if (Math.abs(n - 1/3) < 0.01) {
      imgs.push(`<img src="/static/images/hearts/thirdheart.png" alt="1/3 heart" style="width:28px;height:28px;vertical-align:middle;">`);
    }
    container.innerHTML = imgs.join('');
  }

  // Show current user's hearts
  function showMyHearts() {
    const me = ALL_USERS.find(u => u.email === CURRENT_USER_EMAIL);
    const myHearts = me ? me.hearts : '0';
    renderHearts(document.getElementById('my-hearts'), myHearts);
    document.getElementById('my-hearts-num').textContent = `(${myHearts})`;
  }

  // Show dropdown user's hearts
  function showDropdownHearts() {
    const sel = userSelect.options[userSelect.selectedIndex];
    const hearts = sel.getAttribute('data-hearts') || '0';
    renderHearts(document.getElementById('dropdown-hearts'), hearts);
    document.getElementById('dropdown-hearts-num').textContent = `(${hearts})`;
  }

  userSelect.addEventListener('change', showDropdownHearts);
  showDropdownHearts();
  showMyHearts();

  // Remove auto-render on select change
  // When opening modal, set target_email
  openBtn?.addEventListener("click", function() {
    targetEmailInput.value = userSelect.value;
    checkEvidenceDisabled(userSelect.value);
    modal.classList.remove("hidden");
  });

  // --- user info rendering ---
  function renderUserInfo(email) {
    const user = ALL_USERS.find((u) => u.email === email);
    if (!user) return;
    // Find all evidence for this user
    const evidenceList = EVIDENCE.filter(e => e.target === email);
    let evidenceHtml = "";
    if (evidenceList.length > 0) {
      evidenceHtml = `<div style='margin-top:1em;'><b>Evidence submitted for this user:</b><div style='display:flex;flex-direction:column;align-items:center;gap:0.5em;margin-top:0.5em;'>` +
        evidenceList.map(function(e) {
          return `<div style='background:rgba(255,255,255,0.07);border-radius:6px;padding:0.5em 1em;max-width:350px;text-align:center;'><b>By:</b> ${e.assassin}${e.comments ? `<br><span style='color:#ccc;font-size:0.95em;'>Comment: ${e.comments}</span>` : ''}</div>`;
        }).join('') +
        `</div></div>`;
    } else {
      evidenceHtml = `<div style='margin-top:1em;'><i>No evidence submitted for this user yet.</i></div>`;
    }
    // Responsive image size
    let imgSize = 160;
    if (window.innerWidth > 900) imgSize = 220;
    else if (window.innerWidth > 600) imgSize = 180;
    // Loading spinner (CSS)
    let spinnerHtml = `<div id="img-loading-spinner" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:40px;height:40px;display:flex;align-items:center;justify-content:center;">
      <div class="loader-circle"></div>
    </div>`;
    // If user has 0 hearts, show cannot be eliminated message
    let hearts = parseFloat(user.hearts || "0");
    let submitForm = "";
    if (hearts === 0) {
      submitForm = `<div style='margin-top:1.5em;font-weight:bold;color:#ffb3b3;'>This user cannot be eliminated at the moment.</div>`;
    } else {
      let already = EVIDENCE.some(e => e.assassin === CURRENT_USER_EMAIL && e.target === user.email);
      submitForm = `
        <form id="evidence-form" method="post" enctype="multipart/form-data" style="margin-top:1.5em;display:flex;flex-direction:column;align-items:center;gap:0.5em;max-width:350px;">
          <label for="video" style="width:100%;text-align:left;">Video Evidence (max 25MB):</label>
          <input type="file" name="video" id="video" accept="video/*" required style="width:100%;">
          <label for="comments" style="width:100%;text-align:left;">Comments:</label>
          <textarea name="comments" id="comments" rows="3" placeholder="Optional..." style="width:100%;border-radius:6px;"></textarea>
          <input type="hidden" name="target_email" id="target_email" value="${user.email}">
          <input type="hidden" name="user_email" value="${CURRENT_USER_EMAIL}">
          <div id="progress-container" class="hidden" style="width:100%;"><div id="upload-progress" style="height:8px;background:#fff;width:0%;border-radius:4px;"></div></div>
          <p id="upload-msg" class="upload-msg"></p>
          <button type="submit" class="submit-btn" id="submit-evidence-btn" style="width:100%;" ${already ? 'disabled' : ''}>${already ? 'Already Submitted' : 'Submit Evidence'}</button>
        </form>
      `;
    }
    // Hearts row in user info
    let heartsHtml = `<div style='display:flex;align-items:center;justify-content:center;gap:0.2em;margin-bottom:0.5em;'>`;
    let n = hearts;
    while (n >= 1) {
      heartsHtml += `<img src="/static/images/hearts/oneheart.png" alt="1 heart" style="width:32px;height:32px;vertical-align:middle;">`;
      n -= 1;
    }
    if (Math.abs(n - 2/3) < 0.01) {
      heartsHtml += `<img src="/static/images/hearts/twothirdheart.png" alt="2/3 heart" style="width:32px;height:32px;vertical-align:middle;">`;
    } else if (Math.abs(n - 1/3) < 0.01) {
      heartsHtml += `<img src="/static/images/hearts/thirdheart.png" alt="1/3 heart" style="width:32px;height:32px;vertical-align:middle;">`;
    }
    heartsHtml += `<span style='margin-left:0.4em;font-size:1.1em;'>(${user.hearts || 0})</span></div>`;
    userInfoDiv.innerHTML = `
      <div style="display:flex;flex-direction:column;align-items:center;">
        <h3 style="margin-bottom:0.5em;">${user.fullName}</h3>
        ${heartsHtml}
        <div style="position:relative;min-height:${imgSize}px;margin-bottom:1em;">
          ${spinnerHtml}
          <img id="profile-pic" src="${user.picture}" alt="Profile Picture" style="display:none;max-width:${imgSize}px;max-height:${imgSize}px;border-radius:8px;box-shadow:0 0 12px #000;" onerror="this.style.display='none'">
        </div>
        <p style="margin:0.5em 0 1em 0;"><b>Height:</b> ${user.feet || ''}'${user.inches || ''}"</p>
        <table style="margin:0 auto 1em auto;min-width:220px;max-width:350px;background:rgba(255,255,255,0.07);border-radius:8px;">
          <thead><tr><th style="padding:0.5em 1em;">Period</th><th style="padding:0.5em 1em;">Class</th></tr></thead>
          <tbody>
            ${(user.schedule||'').split(',').map(function(c,i){return `<tr><td style='padding:0.5em 1em;'>${i+1}</td><td style='padding:0.5em 1em;'>${c||'None'}</td></tr>`;}).join('')}
          </tbody>
        </table>
        ${evidenceHtml}
        ${submitForm}
      </div>
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

  // Loader CSS
  const style = document.createElement('style');
  style.innerHTML = `.loader-circle { border: 4px solid #fff; border-top: 4px solid rgba(255,255,255,0.2); border-radius: 50%; width: 36px; height: 36px; animation: spin 1s linear infinite; }
  @keyframes spin { 0% { transform: rotate(0deg);} 100% { transform: rotate(360deg);} }`;
  document.head.appendChild(style);
});

// Loader CSS
const style = document.createElement('style');
style.innerHTML = `.loader-circle { border: 4px solid #fff; border-top: 4px solid rgba(255,255,255,0.2); border-radius: 50%; width: 36px; height: 36px; animation: spin 1s linear infinite; }
@keyframes spin { 0% { transform: rotate(0deg);} 100% { transform: rotate(360deg);} }`;
document.head.appendChild(style);