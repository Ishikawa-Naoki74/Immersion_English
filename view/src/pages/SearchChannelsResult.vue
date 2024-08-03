<!-- ChannelListComponent.vue -->
<template>
  <q-page>
    <q-card>
      <q-card-section class="text-center">
        <div class="row q-col-gutter-md q-gutter-s">
          <div
            v-for="channel in channelsStore.channels"
            :key="channel.id"
            class="col-xs-12 col-sm-6 col-md-4"
          >
            <q-card flat>
              <q-card-section>
                <img :src="channel.thumbnail" class='channel-icon'>
                <p>{{ channel.title }}</p>
                <p>チャンネル登録者数 {{ channel.subscriberCount }}人</p>
                <p>{{ channel.playlistId }}</p>
              </q-card-section>
              <q-card-section class="flex flex-center">
                <span
                  :class="registeredChannels.has(channel.id) ? 'label bg-black text-white' : 'label bg-primary text-white'"
                  @click="toggleRegistration(channel)"
                >
                  {{ registeredChannels.has(channel.id) ? '登録済み' : 'チャンネル登録' }}
                </span>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { api } from 'boot/axios';
import { useChannelsStore } from 'stores/channels-store';

// TODO storeToRefに置き換える
const channelsStore = useChannelsStore()
const registeredChannels = ref<Set<string>>(new Set());

const registerChannel = async (channel: any) => {
  //TODO JSON形式にしてバックエンドにデータ送信
  try {
    const response = await api.post('channels/', {
      channel_id: channel.id,
      channel_title: channel.title,
      channel_icon_url: channel.thumbnail,
      uploads_playlist_id: channel.playlistId,
    });
    if (response.status === 201) {
      registeredChannels.value.add(channel.id);
    }
  } catch (error) {
    console.error('Error registering channel:', error);
    alert('チャンネルの登録に失敗しました。');
  }
}

const unregisterChannel = async (channel: any) => {
  try {
    //TODO将来的にparamsに変更
    const response = await api.delete(`channels/${channel.id}/`);
    if (response.status === 200) {
      registeredChannels.value.delete(channel.id)}
  } catch (error) {
    console.error('Error unregisterd channel', error);
  
  }
}
const toggleRegistration = (channel: any) => {
  if (registeredChannels.value.has(channel.id)) {
    unregisterChannel(channel);
  } else {
    registerChannel(channel);
  }
}

const getChannelDecks = async () => {
  try {
    const channelDecksResponse = await api.get('channel-decks')
    if (channelDecksResponse.status === 200 && channelDecksResponse.data) {
      channelDecksResponse.data.forEach((channel: any) => {
        registeredChannels.value.add(channel.channel_id);
      })
    } else {
      console.log('Failed to fetch channel decks')
    }
  } catch (error) {
    console.error('Error fetching channles decks', error);
  }
}

onMounted(async () => {
  await getChannelDecks();
})

</script>

<style scoped>
.channel-icon {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
}
.q-card-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.selected-channel {
  border: 6px solid skyblue;
}
</style>

