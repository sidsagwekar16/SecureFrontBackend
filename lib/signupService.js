// // signupService.js
// import { createUserWithEmailAndPassword } from "firebase/auth";
// import { auth } from "./firebaseClient";

// export async function registerAgency({ email, password, name, phone, address, plan }) {
//   try {
//     const userCredential = await createUserWithEmailAndPassword(auth, email, password);
//     const user = userCredential.user;
//     const idToken = await user.getIdToken(); // Get Firebase ID Token
//     console.log(email,password,name,phone,address,plan);
    

//     const response = await fetch("http://127.0.0.1:8000/auth/complete-signup", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({
//         payload: {
//           idToken, // Wrap the token inside 'payload'
//         },
//         agency: {
//           name,
//           contactEmail: email,
//           contactPhone: phone,
//           address,
//           subscriptionPlan: plan,
//         },
//       }),
//     });

//     const data = await response.json();
//     if (!response.ok) throw new Error(data.detail || "Registration failed");

//     return data;
//   } catch (error) {
//     throw error;
//   }
// }



// signupService.js
import { createUserWithEmailAndPassword } from "firebase/auth";
import { auth } from "./firebaseClient";

// 🔧 Main function to call from your signup form
export async function registerAgency({ email, password, name, phone, address, plan }) {
  try {
    // 🔐 Step 1: Register the user using Firebase Auth
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;

    // 🔑 Step 2: Get the Firebase ID token
    const idToken = await user.getIdToken();

    // 🧾 Step 3: Prepare the API request body (flattened correctly!)
    const requestBody = { // ✅ No nested 'payload' key — this is flattened!
      agency: {
        name,
        contactEmail: email,
        contactPhone: phone,
        address,
        subscriptionPlan: plan,
        
      },
     
        idToken, // ✅ Firebase ID token
     
    };

    // 🌐 Step 4: Send to FastAPI backend
    const response = await fetch("https://securefrontbackend.onrender.com/auth/complete-signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestBody), // ✅ Correct JSON format
    });

    const data = await response.json();

    // ❌ Handle failure response
    if (!response.ok) throw new Error(data.detail || "Registration failed");

    // ✅ Return response if successful
    return data;
  } catch (error) {
    console.error("Signup error:", error.message);
    throw error;
  }
}