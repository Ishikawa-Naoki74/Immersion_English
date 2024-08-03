<template>
  <div>
    <p><input v-model='email' type='email' placeholder='メールアドレスを入力してください'/></p>
    <p><input v-model='password' type='password' placeholder='パスワードを入力してください'/></p>
    <p><button @click='register'>アカウント登録</button></p>
    <p>すでにアカウントをお持ちですか？<router-link to='/login'>ログイン</router-link></p>
    <p><button @click='registerWithGoogle'>Googleアカウントで新規登録</button></p>
  </div>
</template>

<script setup lang='ts'>
import { createUserWithEmailAndPassword, GoogleAuthProvider, signInWithPopup } from 'firebase/auth';
import { auth } from 'boot/firebase';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const email = ref('');
const password = ref('');
const router = useRouter();
const provider = new GoogleAuthProvider();

// メールアドレス・パスワードでアカウント作成
const register = async () => {
  try {
    await createUserWithEmailAndPassword(auth, email.value, password.value);
    alert('Account created successfully');
  } catch (error) {
    // TODO エラーメッセージの実装
    alert(error.message);
  }
};

// Googleアカウントでアカウント作成
const registerWithGoogle = async () => {
try {
  const result = await signInWithPopup(auth, provider);
  const user = result.user;
  alert('Google login successfully');
  router.push({ name: 'dashboard' });
} catch (error) {
  alert(error.message);
}
};
</script>
