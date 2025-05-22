// static/js/login.js

import { initializeApp } from "https://www.gstatic.com/firebasejs/9.13.0/firebase-app.js";
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  setPersistence,
  inMemoryPersistence,
} from "https://www.gstatic.com/firebasejs/9.13.0/firebase-auth.js";

// Firebase config
const firebaseConfig = {
  apiKey: "AIzaSyAtvSYdz_ujcSaKu-0M8TVNKrPGfIYegMw",
  authDomain: "stuyseniorassassin-60561.firebaseapp.com",
  projectId: "stuyseniorassassin-60561",
};

// Initialize Firebase app and auth
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();
provider.setCustomParameters({ prompt: 'select_account' });

// Initialize persistence once at startup
setPersistence(auth, inMemoryPersistence).catch(err =>
  console.error("Persistence setup failed", err)
);
// Function to handle login and post-login logic
async function loginAndVerify() {
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
	try{

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

    // Redirect after login
    const redirectTo = localStorage.getItem("postLoginRedirect") || "/";
    localStorage.removeItem("postLoginRedirect");
    window.location.href = redirectTo;
  } catch (err) {
    console.error("❌ Login failed:", err);
    // try one more time in case of popup blocked
    alert("Login failed. Make sure your browser does not block popups. Confirm that you are using a senior stuy.edu email account.");
  }
}

// Attach login function to button
document.getElementById("login")?.addEventListener("click", () => {
  localStorage.setItem("postLoginRedirect", "/signup");
  loginAndVerify();
});

(function() {
  const countdownEl = document.getElementById('countdown');
  function update() {
    // May 20, 2025 00:00 EST (UTC-4)
    const target = new Date('2025-05-22T00:00:00-04:00');
    const now = new Date();
    let diff = target - now;
    if (diff <= 0) {
      countdownEl.textContent = 'Signup period has ended.';
      return;
    }
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    diff %= 1000 * 60 * 60 * 24;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    diff %= 1000 * 60 * 60;
    const minutes = Math.floor(diff / (1000 * 60));
    diff %= 1000 * 60;
    const seconds = Math.floor(diff / 1000);
    countdownEl.textContent = `${days}d ${hours}h ${minutes}m ${seconds}s left to sign up`;
  }
  update();
  setInterval(update, 1000);
})();
