<template>
  <div>
    <p><input v-model="email" type="email" placeholder="メールアドレスを入力してください"/></p>
    <p><input v-model="password" type="password" placeholder="パスワードを入力してください"/></p>
    <p><button @click="register">アカウント登録</button></p>
    <p>すでにアカウントをお持ちですか？<router-link to="/login">ログイン</router-link></p>
    <p><button @click="signWithGoogle">Sign in with Google</button></p>
  </div>
</template>

<script setup>
import { createUserWithEmailAndPassword } from "firebase/auth";
import { auth } from "../../firebase/config.ts";
import { ref } from "vue";
import { useRouter } from "vue-router";

const email = ref("");
const password = ref("");
// TODO routerの設定がいるかどうかわからない
const router = useRouter();

const register = () => {
  createUserWithEmailAndPassword(auth, email.value, password.value)
  .then((data) => {
    console.log("Successfully registered");
    //ログイン後にホーム画面に遷移させる
    //router.push('immersion-english')
  })
  .catch((error) => {
    console.log(error.code);
    alert(error.message);
  });
};
</script>
