// static/js/login.js

// Import Firebase modules from the CDN (adjust the version if needed)
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.13.0/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithRedirect, getRedirectResult } from "https://www.gstatic.com/firebasejs/9.13.0/firebase-auth.js";

// Firebase configuration – replace the placeholders with your Firebase project settings.
const firebaseConfig = {
    apiKey: "AIzaSyAtvSYdz_ujcSaKu-0M8TVNKrPGfIYegMw", // Replace with your API key
    authDomain: "stuyseniorassassin-60561.firebaseapp.com", // Replace with your Auth domain
    projectId: "stuyseniorassassin-60561", // Replace with your project ID
    // You can include additional configuration parameters as needed.
};

// Initialize Firebase
const firebaseApp = initializeApp(firebaseConfig);
const auth = getAuth(firebaseApp);
const provider = new GoogleAuthProvider();

// Function to initiate Google login via Firebase.
function onLoginButtonClick() {
    signInWithRedirect(auth, provider);
}

// Function to handle the redirect result after login.
async function handleAuthRedirect() {
    try {
        const result = await getRedirectResult(auth);
        if (result) {
            const idToken = await result.user.getIdToken();
            
            // Send the ID token to the FastAPI backend for verification.
            const response = await fetch("http://localhost:8000/auth/login/verify", {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${idToken}`,
                    "Content-Type": "application/json"
                }
            });
            
            const data = await response.json();
            console.log("Authenticated:", data);

            // Redirect to a protected page or your desired destination.
            window.location.href = "/target"; // Change this to your final destination
        }
    } catch (error) {
        console.error("Error handling auth redirect:", error);
    }
}

// Attach the login button click listener.
document.getElementById("login").addEventListener("click", onLoginButtonClick);

// Call the handler to check if we're on the redirect callback page.
// If the user has just returned from the login flow, this will process the token.
handleAuthRedirect();