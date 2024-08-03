<template>
  <div class="sidebar-item">
    <Icon :name="icon" :color="iconColor" />
    <Text :text="label" :class-name="labelClass" />
  </div>
</template>

<script setup lang="ts">
import Icon from '../atoms/Icon.vue';
import Text from '../atoms/Text.vue';

defineProps<{
  icon: string;
  label: string;
  iconColor?: string;
  labelClass?: string;
}>();
</script>

<style scoped>
.sidebar-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
