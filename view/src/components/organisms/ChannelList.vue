<template>
  <div class="channel-list">
    <div class="channel-list-header">
      <Text class="channel-list-title">チャンネル登録一覧</Text>
    </div>
    <div class="channel-items">
      <div 
        v-for="channel in channels"
        :key="channel.channel_id"
        class="channel-item"
        @click="$router.push(`/channel-videos/${channel.channel_id}`)"
      >
        <q-avatar size="24px">
          <img :src="channel.channel_icon_url" :alt="channel.channel_title" />
        </q-avatar>
        <span class="channel-name">{{ channel.channel_title }}</span>
      </div>
    </div>
    <Divider v-if="showDivider"/>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import Text from '../atoms/Text.vue';
import Divider from '../atoms/Divider.vue';
import { useChannelDecks } from 'src/composables/useChannelDecks';

defineProps<{
  showDivider?: boolean;
}>();

const { channelDecks, getChannelDecks } = useChannelDecks();

const channels = channelDecks;

onMounted(() => {
  getChannelDecks();
});
</script>

<style scoped lang="sass">
.channel-list
  padding: 8px 0

.channel-list-header
  padding: 0 24px 8px 24px

.channel-list-title
  font-size: 14px
  font-weight: 500
  color: #606060

.channel-items
  display: flex
  flex-direction: column
  gap: 4px
  padding: 0 12px

.channel-item
  display: flex
  align-items: center
  padding: 6px 12px
  border-radius: 4px
  cursor: pointer
  transition: background-color 0.2s

  &:hover
    background-color: #f2f2f2

  .q-avatar
    border-radius: 50%
    margin-right: 12px

  .channel-name
    font-size: 14px
    color: #0f0f0f
    font-weight: 400
    flex: 1
    overflow: hidden
    text-overflow: ellipsis
    white-space: nowrap
</style>