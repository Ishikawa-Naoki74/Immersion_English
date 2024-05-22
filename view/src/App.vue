<template>
  <v-app>
    <v-main>
      <!--router-linkで遷移した際に対象のコンポーネントが見込まれる箇所-->>
      <router-view />
    </v-main>
  </v-app>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "App",

  data() {
    return {
      //
    };
  },
});
</script>
