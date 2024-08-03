<template>
  <span :class="className">{{ text }}</span>
</template>

<script setup lang="ts">
defineProps<{
  text: string;
  className?: string;
}>();
</script>
