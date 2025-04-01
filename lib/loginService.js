// create file loginService.js
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "./firebaseClient";

export async function loginAgency(email, password) {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const idToken = await userCredential.user.getIdToken();

    // Send token to your FastAPI backend
    const response = await fetch(`https://securefrontbackend.onrender.com/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ idToken }),
    });

    const data = await response.json();

    if (!response.ok) throw new Error(data.detail || "Login failed");

    // Store agencyId + token in localStorage or cookie
    localStorage.setItem("agencyId", data.agencyId);
    localStorage.setItem("uid", data.uid);
    localStorage.setItem("token", idToken);

    return data;
  } catch (error) {
    throw error;
  }
}