// static/js/login.js

import { initializeApp } from "https://www.gstatic.com/firebasejs/9.13.0/firebase-app.js";
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
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

// Function to handle login and post-login logic
async function loginAndVerify() {
  try {
    // Trigger Google sign-in popup
    const result = await signInWithPopup(auth, provider);
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
    alert("Login failed. Please try again.");
  }
}

// Attach login function to button
document.getElementById("login")?.addEventListener("click", () => {
  localStorage.setItem("postLoginRedirect", "/signup");
  loginAndVerify();
});