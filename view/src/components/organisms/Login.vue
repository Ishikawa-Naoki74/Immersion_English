<template>
  <div>
    <h1>ログイン</h1>
    <p><input v-model="email" type="email" placeholder="メールアドレスを入力してください"/></p>
    <p><input v-model="password" type="password" placeholder="パスワードを入力してくさださい"/></p>
    <p>パスワードを忘れた方はこちら<router-link to="/password-reset">パスワード再設定</router-link></p>
    <p><button @click="login">ログイン</button></p>
    <p>アカウントをお持ちではありませんか？<router-link to="/register">アカウント登録</router-link></p>
    <p><button @click="loginWithGoogle">Googleでログイン</button></p>
  </div>
</template>

<script setup lang="ts">
import { signInWithEmailAndPassword, GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import { auth } from "../../firebase/config";
import { ref } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";

const email = ref("");
const password = ref("")
const router = useRouter();
const provider = new GoogleAuthProvider();

// メールアドレス・パスワードでログイン
const login = async () => {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, email.value, password.value)
    const idToken = await userCredential.user.getIdToken(true);
    // // //IDtトークンをサーバーに送信
    await sendTokenToServer(idToken);
    alert("login successfully")
    router.push({ name: "dashboard"});
  } catch (error) {
    // TODO エラーメッセージの実装
    console.log(error.code);
    alert(error.message);
  };
};

//Googleでログイン
const loginWithGoogle = async () => {
  try {
    const result = await signInWithPopup(auth, provider);
    const user = result.user;
    alert("google login successfully");
    router.push({ name: "dashboard" })
  } catch (error) {
    alert(error.message);
  }
}

//IDトークンをサーバーに送信する関数
const sendTokenToServer = async (token: string) => {
  try {
    await axios.post("http://localhost:8000/api/firebase/verify-token",
    {
      token: token
    },
    {
      headers: {
        "Content-Type": "application/json"
      }
    });
    console.log("sended Token to server!!");
  } catch (error) {
    console.log("Failed token sender to server", error);
  }
}
</script>
<style></style>
