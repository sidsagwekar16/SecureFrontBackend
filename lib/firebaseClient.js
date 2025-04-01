// create file firebaseClient.js
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyBQnLmhyklHc4x_ox7rFbiEpMUk7cgwk_4",
  authDomain: "front-a7a45.firebaseapp.com",
  projectId: "front-a7a45",
  storageBucket: "front-a7a45.firebasestorage.app",
  messagingSenderId: "15311457690",
  appId: "1:15311457690:web:560fd0531ae95b9a38fe23",
  measurementId: "G-LVKKYWBYS9"
};


const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

export { auth };