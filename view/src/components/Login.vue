<template>
  <div class="login-container">
    <h1>Login</h1>
    <input v-model="email" type="email" placeholder="Enter your email"/>
    <input v-model="password" type="password" placeholder="Enter your password"/>
    <button @click="login">Login</button>
  </div>
</template>

<script>
import { auth } from '../firebase/config';

export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: ''
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
    }
  }
};
</script>

<style>
.login-container {
  max-width: 300px;
  margin: auto;
  padding: 20px;
  text-align: center;
}
</style>
