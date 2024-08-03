<template>
  <div v-if="channelDecks && channelDecks.length" class="q-pa-md">
    <q-markup-table flat bordered>
      <thead class="bg-teal table-size">
        <tr>
          <th colspan="5">
            <div class="row no-wrap items-center">
              <div class="text-h4 q-ml-md text-white">Treats</div>
            </div>
          </th>
        </tr>
        <tr>
          <th class="text-left">チャンネル</th>
          <th class="text-left">総学習時間</th>
          <th class="text-left">新規</th>
          <th class="text-left">習得中</th>
          <th class="text-left">復習</th>
        </tr>
      </thead>
      <!--TODO キャッシュに対応させる-->
      <tbody :class="$q.dark.isActive ? 'bg-grey-9' : 'bg-grey-3'">
        <tr v-for="channelDeck in channelDecks" :key="channelDeck.channel_id">
          <td class="text-left">
          <router-link to="/video-decks">
            <img :src='channelDeck.channel_icon_url' class="channel-icon">
          </router-link>
        </td>
          <td class="text-left">{{ channelDeck.total_study_time }}時間</td>
          <td class="text-left">{{ channelDeck.total_new_cards }}</td>
          <td class="text-left">{{ channelDeck.total_learning_cards }}</td>
          <td class="text-left">{{ channelDeck.total_review_cards }}</td>
            <q-btn @click="getChannelVideos(channelDeck.uploads_playlist_id)" label="動画を追加" color="primary" />
        </tr>
      </tbody>
    </q-markup-table>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router'
import { useChannelDecks } from '../composables/useChannelDecks';

const router = useRouter()
const { channelDecks, getChannelDecks } = useChannelDecks();

const getChannelVideos = (uploadsPlaylistId: string) => {
  router.push({ name: 'channel-videos', query: { playlist_id:  uploadsPlaylistId }})
 }

onMounted(async () => {
  await getChannelDecks();
})


</script>

<style scoped>
.q-pa-md {
  max-width: 2000px;
  width: 100%;
  display: flex;
  justify-content: center;
}

.channel-icon {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
}
</style>
