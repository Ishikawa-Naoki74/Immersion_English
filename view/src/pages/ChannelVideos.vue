<template>
  <div class="q-pa-md">
    <h2>チャンネル動画</h2>
    <div v-if="isLoading">読み込み中...</div>
    <div v-else-if="videos.length" class="row q-col-gutter-md">
      <div v-for="video in videos" :key="video.id" class="col-12 col-sm-6 col-md-4">
        <q-card @click="playVideo(video)">
          <div v-if="!video.isPlaying">
            <q-img
              :src="video.thumbnail"
              :ratio="16/9"
              class="cursor-pointer"
            >
              <div class="absolute-center">
                <q-icon name="play_arrow" size="3em" color="white" />
              </div>
              <div class="absolute-bottom text-subtitle2 text-center bg-transparent">
                {{ video.title }}
              </div>
            </q-img>
          </div>
          <q-video
            v-else
            :src="`https://www.youtube.com/embed/${video.id}`"
            :ratio="16/9"
          />
          <q-card-section v-if="!video.isPlaying">
            <div class="text-subtitle2">{{ video.published_at }}</div>
          </q-card-section>
        </q-card>
      </div>
    </div>
    <div v-else>
      動画が見つかりません。
    </div>
    <div class="pagination-container">
    <q-pagination
      v-model="currentPage"
      :max="totalPages"
      :max-pages="10"
      boundary-numbers
      boundary-links
      direction-links
      push
      color="teal"
      active-design="push"
      active-color="orange"
      @update:model-value="handlePageChange"
    />
  </div>
</div>
</template>


<script setup lang="ts">
import { onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useChannelVideos } from '../composables/useChannelVideos';

const route = useRoute();
const {
  videos,
  currentPage,
  totalPages,
  isLoading,
  getChannelVideos,
  playVideo
} = useChannelVideos();

const handlePageChange = (page: number) => {
  console.log('Page changed to:', page);
  getChannelVideos(page);
};

watch(videos, (newVideos) => {
  console.log('Videos updated:', newVideos);
});

onMounted(() => {
  console.log('Component mounted');
  if (route.query.playlist_id) {
    console.log('Fetching videos for playlist:', route.query.playlist_id);
    getChannelVideos(1);
  } else {
    console.error('No playlist_id provided in the route');
  }
});
</script>

<style scoped>
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
