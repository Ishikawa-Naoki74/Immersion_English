<template>
  <div class="q-pa-md">
    <!-- 動画選択画面 -->
    <div v-if="!selectedVideo">
      <div class="row justify-between items-center q-mb-md">
        <h2>動画デッキ ({{ registeredVideos.length }}個の動画)</h2>
        <div class="row q-gutter-sm">
          <q-btn 
            flat 
            icon="arrow_back" 
            label="チャンネル一覧へ"
            @click="$router.push('/channel-decks')"
          />
        </div>
      </div>
      
      <div v-if="isLoading" class="text-center">
        <q-spinner size="50px" color="primary" />
        <p>読み込み中...</p>
      </div>
      
      <div v-else-if="registeredVideos.length" class="row q-col-gutter-md">
        <div v-for="video in registeredVideos" :key="video.video_id" class="col-12 col-sm-6 col-md-4">
          <q-card class="registered-video-card">
            <q-img
              :src="`https://img.youtube.com/vi/${video.video_id}/hqdefault.jpg`"
              :ratio="16/9"
              class="cursor-pointer"
              @click="selectVideo(video)"
            >
              <div class="absolute-center">
                <q-icon name="play_arrow" size="3em" color="white" />
              </div>
            </q-img>
            
            <q-card-section>
              <div class="text-subtitle2 text-weight-medium">
                動画ID: {{ video.video_id }}
              </div>
              <div class="text-body2 text-grey-6 q-mt-xs">
                チャンネル: {{ video.channel_id }}
              </div>
              <div class="text-body2 text-grey-6 q-mt-sm">
                学習時間: {{ video.total_study_time }}分
              </div>
              <div class="row q-mt-sm">
                <div class="col-4 text-center">
                  <div class="text-caption text-grey-6">新規</div>
                  <div class="text-h6 text-blue">{{ video.total_new_cards }}</div>
                </div>
                <div class="col-4 text-center">
                  <div class="text-caption text-grey-6">学習中</div>
                  <div class="text-h6 text-orange">{{ video.total_learning_cards }}</div>
                </div>
                <div class="col-4 text-center">
                  <div class="text-caption text-grey-6">復習</div>
                  <div class="text-h6 text-green">{{ video.total_review_cards }}</div>
                </div>
              </div>
            </q-card-section>
            
            <q-card-actions align="right">
              <q-btn 
                flat 
                color="negative" 
                label="削除"
                @click="removeVideo(video)"
              />
            </q-card-actions>
          </q-card>
        </div>
      </div>
      
      <div v-else class="text-center q-mt-xl">
        <q-icon name="video_library" size="100px" color="grey-4" />
        <p class="text-h6 text-grey-6 q-mt-md">動画が登録されていません</p>
        <p class="text-body2 text-grey-6">チャンネルから動画を追加してください</p>
        <q-btn 
          color="primary" 
          label="チャンネル一覧へ"
          @click="$router.push('/channel-decks')"
        />
      </div>
    </div>

    <!-- 動画再生画面 -->
    <div v-else>
      <div class="row justify-between items-center q-mb-md">
        <h2>動画再生</h2>
        <div class="row q-gutter-sm">
          <q-btn 
            flat 
            icon="arrow_back" 
            label="戻る"
            @click="selectedVideo = null"
          />
        </div>
      </div>

      <!-- 動画プレイヤー（小さいサイズ） -->
      <div class="video-container-small q-mb-md">
        <iframe
          :src="`https://www.youtube.com/embed/${selectedVideo.video_id}?enablejsapi=1&modestbranding=1&rel=0`"
          frameborder="0"
          allowfullscreen
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          class="video-player"
          @click.stop
        ></iframe>
      </div>

      <!-- 動画情報（折りたたみ可能） -->
      <div class="video-info q-mt-md">
        <q-card>
          <q-card-section class="q-pa-sm">
            <div class="row justify-between items-center cursor-pointer" @click="showVideoInfo = !showVideoInfo">
              <div class="text-subtitle1 text-weight-medium">動画情報</div>
              <q-icon
                :name="showVideoInfo ? 'expand_less' : 'expand_more'"
                size="sm"
              />
            </div>
          </q-card-section>

          <q-separator v-if="showVideoInfo" />

          <q-card-section v-if="showVideoInfo">
            <div class="text-body2 text-grey-6 q-mb-sm">
              動画ID: {{ selectedVideo.video_id }}
            </div>
            <div class="text-body2 text-grey-6 q-mb-sm">
              学習時間: {{ selectedVideo.total_study_time }}分
            </div>
            <div class="row q-mt-sm">
              <div class="col-4 text-center">
                <div class="text-caption text-grey-6">新規</div>
                <div class="text-h6 text-blue">{{ selectedVideo.total_new_cards }}</div>
              </div>
              <div class="col-4 text-center">
                <div class="text-caption text-grey-6">学習中</div>
                <div class="text-h6 text-orange">{{ selectedVideo.total_learning_cards }}</div>
              </div>
              <div class="col-4 text-center">
                <div class="text-caption text-grey-6">復習</div>
                <div class="text-h6 text-green">{{ selectedVideo.total_review_cards }}</div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- 字幕表示（常に表示） -->
      <div class="subtitles-section q-mt-md">
        <q-card>
          <q-card-section>
            <div class="row justify-between items-center q-mb-md">
              <div class="text-h6">字幕</div>
              <div class="row q-gutter-sm">
                <q-btn 
                  flat 
                  :color="isLoadingSubtitles ? 'grey' : 'primary'"
                  :loading="isLoadingSubtitles"
                  :label="subtitles ? '字幕を再取得' : '字幕を取得'"
                  @click="fetchSubtitles"
                />
                <q-select
                  v-if="subtitles && Object.keys(subtitles).length > 0"
                  v-model="selectedSubtitleLanguage"
                  :options="subtitleLanguageOptions"
                  label="言語"
                  dense
                  style="min-width: 100px"
                />
              </div>
            </div>
            
            <div v-if="isLoadingSubtitles" class="text-center q-py-md">
              <q-spinner size="30px" color="primary" />
              <p class="text-body2 text-grey-6 q-mt-sm">字幕を取得中...</p>
            </div>
            
            <div v-else-if="subtitles && Object.keys(subtitles).length > 0" class="subtitle-content">
              <!-- 言語切り替えタブ -->
              <div class="language-tabs q-mb-md">
                <q-btn-toggle
                  v-model="selectedSubtitleLanguage"
                  :options="subtitleLanguageOptions.map(opt => ({ label: opt.label, value: opt.value }))"
                  color="primary"
                  text-color="primary"
                  flat
                  stretch
                />
              </div>
              
              <div v-if="getCurrentSubtitleData()" class="q-mb-sm">
                <q-chip 
                  :color="getSourceColor(getCurrentSubtitleData().source)"
                  text-color="white"
                  size="sm"
                >
                  {{ getSourceText(getCurrentSubtitleData().source) }}
                  {{ selectedSubtitleLanguage === 'english' ? '英語' : selectedSubtitleLanguage === 'japanese' ? '日本語' : 'その他' }}
                </q-chip>
              </div>
              
              <div class="subtitle-text">
                <div v-if="showDetailedSubtitles" class="subtitle-entries">
                  <div 
                    v-for="(entry, index) in getCurrentSubtitleData()?.transcript" 
                    :key="index"
                    class="subtitle-entry q-mb-xs"
                  >
                    <span class="time-stamp text-caption text-grey-6">
                      {{ formatTime(entry.start) }} - {{ formatTime(entry.start + entry.duration) }}
                    </span>
                    <p class="subtitle-line q-ma-none q-ml-sm">{{ entry.text }}</p>
                  </div>
                </div>
                <div v-else class="subtitle-full-text">
                  {{ getCurrentSubtitleData()?.text }}
                </div>
              </div>
              
              <div class="row justify-between q-mt-md">
                <q-btn
                  flat
                  size="sm"
                  :label="showDetailedSubtitles ? '全文表示' : '詳細表示'"
                  @click="showDetailedSubtitles = !showDetailedSubtitles"
                />
                <div class="text-caption text-grey-6">
                  {{ getCurrentSubtitleData()?.transcript?.length || 0 }}個のエントリ
                </div>
              </div>
            </div>
            
            <div v-else-if="subtitleError" class="text-center q-py-md">
              <q-icon name="error" size="40px" color="negative" />
              <p class="text-body2 text-negative q-mt-sm">{{ subtitleError }}</p>
              <q-btn 
                outline
                color="primary"
                label="再試行"
                @click="fetchSubtitles"
                class="q-mt-sm"
              />
            </div>
            
            <div v-else class="text-center q-py-md">
              <q-icon name="subtitles" size="40px" color="grey-4" />
              <p class="text-body2 text-grey-6 q-mt-sm">動画を選択すると自動的に字幕を取得します</p>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { api } from 'boot/axios';

interface RegisteredVideo {
  video_id: string;
  total_study_time: number;
  total_new_cards: number;
  total_learning_cards: number;
  total_review_cards: number;
  created_at: string;
}

const route = useRoute();
const registeredVideos = ref<RegisteredVideo[]>([]);
const isLoading = ref(false);
const selectedVideo = ref<RegisteredVideo | null>(null);

// 字幕関連の状態
const subtitles = ref<any>(null);
const isLoadingSubtitles = ref(false);
const subtitleError = ref<string | null>(null);
const selectedSubtitleLanguage = ref<string>('english');
const showDetailedSubtitles = ref(false);

// 動画情報の表示/非表示
const showVideoInfo = ref(false);

const getRegisteredVideos = async (channelId?: string) => {
  isLoading.value = true;
  try {
    console.log('Fetching registered videos for channel:', channelId);
    
    const response = await api.get('videos/');
    console.log('API response:', response.data);
    
    if (response.status === 200) {
      let videos = response.data;
      
      // Filter by channel_id if specified
      if (channelId) {
        videos = videos.filter((video: any) => video.channel_id === channelId);
        console.log('Filtered videos for channel:', videos);
      }
      
      registeredVideos.value = videos;
      console.log('Final videos to display:', registeredVideos.value.length, 'videos');
    }
  } catch (error) {
    console.error('Error fetching registered videos:', error);
    alert('ビデオの取得に失敗しました: ' + error);
  } finally {
    isLoading.value = false;
  }
};

const selectVideo = async (video: RegisteredVideo) => {
  selectedVideo.value = video;
  // 動画が変更されたら字幕をリセット
  subtitles.value = null;
  subtitleError.value = null;
  selectedSubtitleLanguage.value = 'english';
  
  // 動画選択時に自動的に字幕を取得
  console.log('動画選択時に字幕を自動取得開始:', video.video_id);
  await fetchSubtitles();
};

const removeVideo = async (video: RegisteredVideo) => {
  try {
    console.log('Removing video:', video.video_id);
    
    const response = await api.delete(`videos/${video.video_id}/`);
    
    if (response.status === 204) {
      console.log('Video deleted successfully');
      registeredVideos.value = registeredVideos.value.filter(v => v.video_id !== video.video_id);
      
      // 削除された動画が選択されている場合は選択を解除
      if (selectedVideo.value?.video_id === video.video_id) {
        selectedVideo.value = null;
      }
    }
  } catch (error) {
    console.error('Error removing video:', error);
    alert('動画の削除に失敗しました');
  }
};

// 字幕取得機能
const fetchSubtitles = async () => {
  if (!selectedVideo.value) return;
  
  isLoadingSubtitles.value = true;
  subtitleError.value = null;
  
  try {
    console.log('Fetching subtitles for video:', selectedVideo.value.video_id);
    
    const response = await api.get(`videos/${selectedVideo.value.video_id}/transcript/`);
    
    if (response.status === 200) {
      subtitles.value = response.data.subtitles;
      console.log('Subtitles fetched:', subtitles.value);
      
      // 利用可能な言語を確認して最初の言語を選択
      if (subtitles.value.english) {
        selectedSubtitleLanguage.value = 'english';
      } else if (subtitles.value.japanese) {
        selectedSubtitleLanguage.value = 'japanese';
      }
    }
  } catch (error: any) {
    console.error('Error fetching subtitles:', error);
    subtitleError.value = error.response?.data?.error || '字幕の取得に失敗しました';
  } finally {
    isLoadingSubtitles.value = false;
  }
};

// 字幕言語のオプション
const subtitleLanguageOptions = computed(() => {
  if (!subtitles.value) return [];
  
  const options = [];
  if (subtitles.value.english) {
    options.push({ label: '英語', value: 'english' });
  }
  if (subtitles.value.japanese) {
    options.push({ label: '日本語', value: 'japanese' });
  }
  return options;
});

// 現在の字幕データを取得
const getCurrentSubtitleData = () => {
  if (!subtitles.value || !selectedSubtitleLanguage.value) return null;
  return subtitles.value[selectedSubtitleLanguage.value];
};

// 時間フォーマット関数
const formatTime = (seconds: number) => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

// ソース色を取得
const getSourceColor = (source: string) => {
  if (source === 'original') return 'positive';
  if (source === 'auto-generated') return 'info';
  if (source.startsWith('translated')) return 'warning';
  return 'grey';
};

// ソーステキストを取得
const getSourceText = (source: string) => {
  if (source === 'original') return 'オリジナル';
  if (source === 'auto-generated') return '自動生成';
  if (source === 'translated_from_english') return '英語から翻訳';
  if (source === 'translated_from_japanese') return '日本語から翻訳';
  if (source.startsWith('translated_from_')) return '翻訳';
  return source;
};

onMounted(() => {
  // URLからチャンネルIDを取得
  const channelId = route.query.channel_id as string;
  getRegisteredVideos(channelId);
});
</script>

<style scoped>
.registered-video-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.registered-video-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.registered-video-card .q-img {
  position: relative;
  overflow: hidden;
}

.registered-video-card .q-img::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(0,0,0,0.1), rgba(0,0,0,0.3));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.registered-video-card:hover .q-img::before {
  opacity: 1;
}

.video-container {
  position: relative;
  width: 100%;
  height: 0;
  padding-bottom: 56.25%; /* 16:9 aspect ratio */
}

/* 小さいサイズの動画コンテナ */
.video-container-small {
  position: relative;
  width: 100%;
  max-width: 640px; /* 最大幅を設定 */
  height: 0;
  padding-bottom: 36%; /* 16:9 aspect ratio for smaller size */
  margin: 0 auto; /* センタリング */
}

.video-player {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

/* 字幕スタイル */
.subtitles-section .subtitle-content {
  max-height: 400px;
  overflow-y: auto;
}

.subtitle-entries {
  background: #f5f5f5;
  border-radius: 8px;
  padding: 16px;
}

.subtitle-entry {
  border-bottom: 1px solid #e0e0e0;
  padding: 8px 0;
}

.subtitle-entry:last-child {
  border-bottom: none;
}

.time-stamp {
  display: block;
  font-weight: 500;
  margin-bottom: 4px;
}

.subtitle-line {
  line-height: 1.5;
  word-break: break-word;
}

.subtitle-full-text {
  background: #f5f5f5;
  border-radius: 8px;
  padding: 16px;
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
}
</style>