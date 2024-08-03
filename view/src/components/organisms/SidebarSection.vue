<template>
  <div class="sidebar-section">
    <SidebarItem
    v-for="item in items"
    :key="item.label"
    :icon="item.icon"
    :label="item.label"
    />
    <Divider v-if="showDivider"/>
  </div>
</template>

<script setup lang="ts">
import SidebarItem from '../molecules/SidebarItem.vue';
import Divider from '../atoms/Divider.vue';

defineProps<{
  title?: string;
  items: Array<{ icon: string; label: string }>
  showDivider?: boolean;
}>()
</script>
