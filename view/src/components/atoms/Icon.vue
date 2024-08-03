<template>
<q-icon :name="name" :color="color" :size="size" />
</template>

<script setup lang="ts">
defineProps<{
  name: string,
  color?: string;
  size?: string;
}>();
</script>
