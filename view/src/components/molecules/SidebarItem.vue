<template>
  <div class="sidebar-item" @click="handleClick">
    <Icon :name="icon" :color="iconColor" />
    <Text :text="label" :class-name="labelClass" />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import Icon from '../atoms/Icon.vue';
import Text from '../atoms/Text.vue';

const props = defineProps<{
  icon: string;
  label: string;
  iconColor?: string;
  labelClass?: string;
  to?: string;
}>();

const router = useRouter();

const handleClick = () => {
  if (props.to) {
    router.push(props.to);
  } else if (props.label === 'Home') {
    router.push('/');
  }
};
</script>

<style scoped>
.sidebar-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.sidebar-item:hover {
  background-color: #f2f2f2;
}
</style>
