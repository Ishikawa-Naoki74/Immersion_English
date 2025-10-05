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
            <div class="q-mt-sm">
              <q-btn
                :class="[
                  'video-registration-btn',
                  registeredVideos.has(video.id) ? 'registered' : 'unregistered'
                ]"
                :loading="loadingVideos.has(video.id)"
                @click.stop="toggleVideoRegistration(video)"
                unelevated
                no-caps
                size="sm"
              >
                <q-icon
                  :name="registeredVideos.has(video.id) ? 'check' : 'add'"
                  class="btn-icon"
                />
                {{ registeredVideos.has(video.id) ? '登録済み' : '動画登録' }}
              </q-btn>
            </div>
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
import { onMounted, watch, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useChannelVideos } from '../composables/useChannelVideos';
import { api } from 'boot/axios';

const route = useRoute();
const {
  videos,
  currentPage,
  totalPages,
  isLoading,
  getChannelVideos,
  playVideo
} = useChannelVideos();

const registeredVideos = ref<Set<string>>(new Set());
const loadingVideos = ref<Set<string>>(new Set());

const getChannelIdFromRoute = () => {
  return route.params.channelId as string || route.query.channel_id as string;
};

const registerVideo = async (video: any) => {
  loadingVideos.value.add(video.id);
  try {
    const channelId = getChannelIdFromRoute();
    const response = await api.post('videos/', {
      video_id: video.id,
      channel_id: channelId,
      total_study_time: 0,
      total_new_cards: 0,
      total_learning_cards: 0,
      total_review_cards: 0,
    });
    if (response.status === 201) {
      registeredVideos.value.add(video.id);
    }
  } catch (error) {
    console.error('Error registering video:', error);
    alert('動画の登録に失敗しました。');
  } finally {
    loadingVideos.value.delete(video.id);
  }
};

const unregisterVideo = async (video: any) => {
  loadingVideos.value.add(video.id);
  try {
    const response = await api.delete(`videos/${video.id}/`);
    if (response.status === 200) {
      registeredVideos.value.delete(video.id);
    }
  } catch (error) {
    console.error('Error unregistering video:', error);
  } finally {
    loadingVideos.value.delete(video.id);
  }
};

const toggleVideoRegistration = (video: any) => {
  if (registeredVideos.value.has(video.id)) {
    unregisterVideo(video);
  } else {
    registerVideo(video);
  }
};

const getRegisteredVideos = async () => {
  try {
    const channelId = getChannelIdFromRoute();
    const response = await api.get('videos/', {
      params: { channel_id: channelId }
    });
    if (response.status === 200 && response.data) {
      response.data.forEach((video: any) => {
        registeredVideos.value.add(video.video_id);
      });
    }
  } catch (error) {
    console.error('Error fetching registered videos:', error);
  }
};

const handlePageChange = (page: number) => {
  console.log('Page changed to:', page);
  getChannelVideos(page);
};

watch(videos, (newVideos) => {
  console.log('Videos updated:', newVideos);
});

const getChannelData = async () => {
  const channelId = getChannelIdFromRoute();
  if (!channelId) {
    console.error('No channel ID found in route');
    return;
  }
  
  try {
    const response = await api.get('channels/', {
      params: { channel_id: channelId }
    });
    if (response.status === 200 && response.data.length > 0) {
      const channelData = response.data[0];
      return channelData.uploads_playlist_id;
    }
  } catch (error) {
    console.error('Error fetching channel data:', error);
  }
  return null;
};

onMounted(async () => {
  console.log('Component mounted');
  await getRegisteredVideos();
  
  const channelId = getChannelIdFromRoute();
  if (channelId) {
    console.log('Fetching videos for channel:', channelId);
    const playlistId = route.query.playlist_id as string || await getChannelData();
    if (playlistId) {
      console.log('Using playlist:', playlistId);
      getChannelVideos(1);
    } else {
      console.error('No playlist_id found for channel');
    }
  } else {
    console.error('No channel ID provided in the route');
  }
});
</script>

<style scoped>
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.video-registration-btn {
  min-width: 100px;
  padding: 6px 12px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  border-radius: 6px;
  font-weight: 500;
  font-size: 12px;
}

.video-registration-btn.unregistered {
  background-color: #1976d2;
  color: white;
}

.video-registration-btn.unregistered:hover {
  background-color: #1565c0;
  transform: translateY(-2px);
  box-shadow: 0 3px 6px rgba(25, 118, 210, 0.3);
}

.video-registration-btn.registered {
  background-color: #4caf50;
  color: white;
}

.video-registration-btn.registered:hover {
  background-color: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 3px 6px rgba(76, 175, 80, 0.3);
}

.video-registration-btn:active {
  transform: translateY(0);
}

.video-registration-btn .btn-icon {
  margin-right: 4px;
  font-size: 14px;
  transition: transform 0.2s ease;
}

.video-registration-btn:hover .btn-icon {
  transform: scale(1.1);
}
</style>
