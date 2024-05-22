// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
// firebaseの初期化
const firebaseConfig = {
  apiKey: "AIzaSyAzU5-KntGGo6FEQ0Ejqh4vle6wiIJ2AJA",
  authDomain: "immersion-english.firebaseapp.com",
  projectId: "immersion-english",
  storageBucket: "immersion-english.appspot.com",
  messagingSenderId: "704525329697",
  appId: "1:704525329697:web:524ef51e134540817b8a60",
  measurementId: "G-V1LKWEB2CC",
};

// firebaseアプリ初期化
const app = initializeApp(firebaseConfig);
// 認証サービスを初期化してエクスポート
export const auth = getAuth(app);
