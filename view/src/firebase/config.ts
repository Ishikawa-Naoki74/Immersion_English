// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyAzU5-KntGGo6FEQ0Ejqh4vle6wiIJ2AJA",
  authDomain: "immersion-english.firebaseapp.com",
  projectId: "immersion-english",
  storageBucket: "immersion-english.appspot.com",
  messagingSenderId: "704525329697",
  appId: "1:704525329697:web:524ef51e134540817b8a60",
  measurementId: "G-V1LKWEB2CC",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
// const analytics = getAnalytics(app);
