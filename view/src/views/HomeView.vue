<template>
  <hello-world />
  <LoginForm />
</template>

<script lang="ts">
import { defineComponent } from "vue";

// Components
import HelloWorld from "../components/HelloWorld.vue";
import LoginForm from "../components/LoginForm.vue"

export default defineComponent({
  name: "HomeView",

  components: {
    HelloWorld,
    LoginForm,
  },
});
</script>
