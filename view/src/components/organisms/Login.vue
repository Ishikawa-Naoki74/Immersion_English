<template>
  <div>
    <h1>ログイン</h1>
    <p><input v-model="email" type="email" placeholder="メールアドレスを入力してください"/></p>
    <p><input v-model="password" type="password" placeholder="パスワードを入力してくさださい"/></p>
    <p>パスワードを忘れた方はこちら<router-link to="/password-reset">パスワード再設定</router-link></p>
    <p><button @click="login">ログイン</button></p>
    <p>アカウントをお持ちではありませんか？<router-link to="/register">アカウント登録</router-link></p>
  </div>
</template>

<script setup>
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "../../firebase/config.ts";
import { ref } from "vue";
import { useRouter } from "vue-router";

const email = ref("");
const password = ref("");
// TODO routerの設定がいるかどうかわからない
const router = useRouter();

const login = () => {
  signInWithEmailAndPassword(auth, email.value, password.value)
  .then((userCredential) => {
    console.log("Successfully login", userCredential);
    //ログイン成功後ホーム画面にリダイレクトさせる
    //router.push('immersion-english')
  })
  .catch((error) {
    console.log(error.code);
    alert(error.message);
  });
};
</script>
<style></style>
