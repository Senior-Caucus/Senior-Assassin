// static/js/login.js

import { initializeApp } from "https://www.gstatic.com/firebasejs/9.13.0/firebase-app.js";
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  setPersistence,
  inMemoryPersistence,
} from "https://www.gstatic.com/firebasejs/9.13.0/firebase-auth.js";

// --- tiny util to test whether sessionStorage works (required by Firebase OAuth) ---
function sessionStorageAvailable() {
  try {
    const k = "__ss_test__";
    sessionStorage.setItem(k, k);
    sessionStorage.removeItem(k);
    return true;
  } catch (_) {
    return false;
  }
}

// Detect common in‑app browsers (e.g. Instagram, Facebook) because they often block pop‑ups
const IN_APP_BROWSER = /Instagram|FBAN|FBAV/i.test(navigator.userAgent);

// Firebase config
const firebaseConfig = {
  apiKey: "AIzaSyAtvSYdz_ujcSaKu-0M8TVNKrPGfIYegMw",
  authDomain: "stuyseniorassassin-60561.firebaseapp.com",
  projectId: "stuyseniorassassin-60561",
};

// Initialize Firebase app and auth
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Ensure we finish setting persistence before anyone can click "login".
const persistenceReady = setPersistence(auth, inMemoryPersistence)
  .catch(err => {
    console.error("Persistence setup failed", err);
  });

const provider = new GoogleAuthProvider();
provider.setCustomParameters({ prompt: 'select_account' });

// Function to handle login and post-login logic
async function loginAndVerify() {
  // Abort early if the environment will break Firebase's OAuth flow.
  if (!sessionStorageAvailable()) {
    alert("This browser blocks session storage, which the login flow needs. Please open the page in Safari, Chrome, or your default browser instead of an in‑app viewer.");
    return;
  }

  if (IN_APP_BROWSER) {
    alert("In‑app browsers (e.g. Instagram) cannot complete Google sign‑in. Tap the ••• menu and choose “Open in browser”, then try again.");
    return;
  }

  // Make sure our chosen persistence mode is fully initialised.
  await persistenceReady;

  let result;
  try {
    result = await signInWithPopup(auth, provider);
  } catch (err) {
    console.error("Firebase auth error:", err);
    switch (err.code) {
      case 'auth/popup-blocked':
        alert("Popup was blocked—disable your blocker or use the redirect flow.");
        break;
      case 'auth/popup-closed-by-user':
        alert("You closed the sign-in popup before completing login.");
        break;
      default:
        alert("Authentication error: " + err.message);
    }
    return;
  }
  try {

    // Trigger Google sign-in popup
    const user = result.user;
    const idToken = await user.getIdToken();

    // Send ID token to FastAPI backend
    const response = await fetch("/auth/login/verify", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${idToken}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) throw new Error("Token verification failed");

    const data = await response.json();
    console.log("✅ Authenticated:", data.email);

    // Save to localStorage (temp solution)
    localStorage.setItem("userEmail", data.email);

    // Always bounce to /login after a successful backend verification
    window.location.href = "/login";
  } catch (err) {
    console.error("❌ Login failed:", err);
    // try one more time in case of popup blocked
    alert("Login failed. Make sure your browser does not block popups. Confirm that you are using a senior stuy.edu email account.");
  }
}

// Attach login function to button
document.getElementById("login")?.addEventListener("click", () => {
  const loginButton = document.getElementById("login");
  if (loginButton) {
    loginButton.disabled = true;
    loginButton.textContent = "Logging in...";
  }
  loginAndVerify()
    .finally(() => {
      // Re‑enable the button if the flow aborted (success will redirect away)
      if (loginButton) {
        loginButton.disabled = false;
        loginButton.textContent = "Login";
      }
    });
});
