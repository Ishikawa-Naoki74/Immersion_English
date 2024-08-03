<template>
  <q-separator :color="color" :size="size" />
</template>

<script setup lang="ts">
defineProps<{
  color?: string;
  size?: string;
}>()
</script>
