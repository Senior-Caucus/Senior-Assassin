// Assume Firebase is already initialized.
import { getAuth, GoogleAuthProvider, signInWithRedirect, getRedirectResult } from "firebase/auth";

const auth = getAuth();
const provider = new GoogleAuthProvider();

function onLoginButtonClick() {
  // Trigger Firebase redirect sign-in.
  signInWithRedirect(auth, provider);
}

// In your callback page:
async function handleAuthRedirect() {
  console.log("Handling auth redirect...");

  const result = await getRedirectResult(auth);
  if (result) {
    const idToken = await result.user.getIdToken();
    
    // Send the token to the FastAPI backend for verification.
    const response = await fetch("http://localhost:8000/auth/login/verify", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${idToken}`,
        "Content-Type": "application/json"
      }
    });
    const data = await response.json();
    console.log("Authenticated:", data);

    // Now redirect to your desired final destination.
    alert("Login successful! Redirecting...");
  }
}

// Call this function when the page loads to handle the redirect result.
document.getElementById("login").addEventListener("click", onLoginButtonClick);