<template>
  <div>
    <input
      v-model="email"
      type="email"
      placeholder="メールアドレスを入力してください"
    />
    <input
      v-model="password"
      type="password"
      placeholder="パスワードを入力してください"
    />
    <button @click="register">アカウント登録</button>
    <p>
      すでにアカウントをお持ちですか？
      <router-link to="/login">ログイン</router-link>
    </p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: '',
      password: '',
    };
  },
  methods: {
    register() {
      firebase
        .auth()
        .createUserWithEmailAndPassword(this.email, this.password)
        .then((response) => {
          alert('アカウントが作成されました');
        })
        .catch((error) => {
          alert(error.message);
        });
    },
  },
};
</script>
