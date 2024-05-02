<template>
  <div>
    <h1>ログイン</h1>
    <input
      v-model="email"
      type="email"
      placeholder="メールアドレスを入力してください"
    />
    <input
      v-model="password"
      type="password"
      placeholder="パスワードを入力してくさださい"
    />
    <p>
      パスワードを忘れた方はこちら<router-link to="password-reset"
        >パスワード再設定</router-link
      >
    </p>
    <button @click="login">ログイン</button>
    <p>
      アカウントをお持ちではありませんか？<router-link to="/register"
        >アカウント登録</router-link
      >
    </p>
  </div>
</template>

<script>
import { auth } from '../firebase/config';

export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
    };
  },
  methods: {
    async login() {
      try {
        await auth.signInWithEmailAndPassword(this.email, this.password);
        this.$router.push('/home'); // Redirect to home after login
      } catch (error) {
        alert(error.message);
      }
    },
  },
};
</script>
<style></style>
