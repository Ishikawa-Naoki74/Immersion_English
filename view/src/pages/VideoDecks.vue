<template>
  <div class="q-pa-md">
    <!-- 動画選択画面 -->
    <div v-if="!selectedVideo">
      <div class="row justify-between items-center q-mb-md">
        <h2>動画デッキ</h2>
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

      <!-- 動画プレイヤー -->
      <div class="video-container q-mb-md">
        <iframe
          ref="playerIframe"
          :src="`https://www.youtube.com/embed/${selectedVideo.video_id}?enablejsapi=1&modestbranding=1&rel=0`"
          frameborder="0"
          allowfullscreen
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          class="video-player"
          @click.stop
        ></iframe>
      </div>

      <!-- 字幕リスト（ハイライト & クリックでシーク） -->
      <div v-if="displaySubtitles.length" class="subtitle-list q-mb-md">
        <q-card flat bordered class="q-pa-sm">
          <div class="text-caption text-grey-7 q-mb-xs">
            字幕（クリックでその時間へ移動、テキスト選択でハイライト保存）
          </div>
          <div class="subtitle-scroll">
            <div
              v-for="(sub, idx) in displaySubtitles"
              :key="idx"
              class="subtitle-row"
              :class="{ 'is-current': isCurrentSubtitle(sub) }"
              @click="seekTo(sub.start)"
              @mouseup="handleTextSelection($event, sub)"
            >
              <span class="time">{{ formatTime(sub.start) }}</span>
              <span class="text" :data-start="sub.start">{{ sub.text }}</span>
            </div>
          </div>
        </q-card>
      </div>

      <!-- ハイライト保存ダイアログ -->
      <q-dialog v-model="showHighlightDialog" persistent>
        <q-card style="min-width: 400px">
          <q-card-section>
            <div class="text-h6">ハイライトを保存</div>
          </q-card-section>

          <q-card-section class="q-pt-none">
            <div class="q-mb-md">
              <div class="text-caption text-grey-7">選択したテキスト</div>
              <div class="text-body1 text-weight-medium q-pa-sm bg-grey-2 rounded-borders">
                {{ highlightForm.highlighted_text }}
              </div>
            </div>

            <div class="q-mb-md">
              <div class="text-caption text-grey-7">タイムスタンプ</div>
              <div class="text-body2">{{ formatTime(highlightForm.timestamp) }}</div>
            </div>

            <q-checkbox
              v-model="highlightForm.auto_generate"
              label="意味と語源を自動生成する（Gemini AI）"
              class="q-mb-md"
            />

            <div v-if="isGenerating" class="text-center q-py-md">
              <q-spinner color="primary" size="40px" />
              <div class="text-caption q-mt-sm">AI生成中...</div>
            </div>

            <q-input
              v-model="highlightForm.meaning_japanese"
              label="日本語の意味"
              type="textarea"
              rows="3"
              filled
              class="q-mb-md"
              hint="AIが自動生成するか、手動で入力してください"
            />

            <q-input
              v-model="highlightForm.etymology"
              label="語源"
              type="textarea"
              rows="2"
              filled
              class="q-mb-md"
              hint="AIが自動生成するか、手動で入力してください"
            />

            <div class="q-mb-md">
              <div class="text-caption text-grey-7 q-mb-xs">イメージ画像</div>
              <q-file
                v-model="imageFile"
                label="画像を選択"
                filled
                accept="image/*"
                @update:model-value="handleImageUpload"
                class="q-mb-sm"
              >
                <template v-slot:prepend>
                  <q-icon name="image" />
                </template>
              </q-file>

              <div v-if="highlightForm.image_url" class="q-mt-sm">
                <div class="text-caption q-mb-xs">プレビュー:</div>
                <q-img
                  :src="highlightForm.image_url"
                  style="max-width: 200px; border-radius: 8px;"
                  fit="contain"
                />
                <q-btn
                  flat
                  dense
                  size="sm"
                  color="negative"
                  label="画像を削除"
                  @click="removeImage"
                  class="q-mt-xs"
                />
              </div>
            </div>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat label="キャンセル" color="grey" @click="closeHighlightDialog" />
            <q-btn
              flat
              label="保存"
              color="primary"
              :loading="isSaving"
              @click="saveHighlight"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <!-- 保存済みハイライト数表示 -->
      <div v-if="highlights.length" class="q-mb-md">
        <q-btn
          flat
          color="primary"
          :label="`保存済みハイライト: ${highlights.length}件`"
          icon="bookmark"
          @click="showHighlightListDialog = true"
        />
      </div>

      <!-- ハイライト一覧ダイアログ -->
      <q-dialog v-model="showHighlightListDialog" maximized>
        <q-card>
          <q-card-section class="row items-center q-pb-none">
            <div class="text-h6">保存済みハイライト ({{ highlights.length }}件)</div>
            <q-space />
            <q-btn icon="close" flat round dense @click="showHighlightListDialog = false" />
          </q-card-section>

          <q-card-section class="q-pt-sm">
            <div class="highlights-grid">
              <q-card
                v-for="highlight in highlights"
                :key="highlight.id"
                class="highlight-card"
                flat
                bordered
              >
                <q-card-section class="q-pa-sm">
                  <div class="row items-start justify-between">
                    <div class="col">
                      <div class="text-weight-bold text-body1 ellipsis-2-lines">
                        {{ highlight.highlighted_text }}
                      </div>
                      <div class="text-caption text-grey-7 q-mt-xs">
                        <q-icon name="schedule" size="xs" /> {{ formatTime(highlight.timestamp) }}
                      </div>
                    </div>
                    <div class="col-auto q-ml-sm">
                      <q-btn
                        flat
                        dense
                        round
                        size="sm"
                        icon="play_arrow"
                        color="primary"
                        @click="seekToAndClose(highlight.timestamp)"
                      >
                        <q-tooltip>再生</q-tooltip>
                      </q-btn>
                    </div>
                  </div>

                  <div v-if="highlight.image_url" class="q-mt-sm">
                    <img
                      :src="highlight.image_url"
                      class="highlight-image"
                      @error="handleImageError"
                    />
                  </div>

                  <div v-if="highlight.meaning_japanese" class="q-mt-sm">
                    <div class="text-caption text-weight-bold">意味:</div>
                    <div class="text-caption ellipsis-3-lines">{{ highlight.meaning_japanese }}</div>
                  </div>

                  <div v-if="highlight.etymology" class="q-mt-sm">
                    <div class="text-caption text-weight-bold">語源:</div>
                    <div class="text-caption ellipsis-2-lines">{{ highlight.etymology }}</div>
                  </div>

                  <div class="row q-mt-sm q-gutter-xs">
                    <q-btn
                      flat
                      dense
                      size="sm"
                      icon="edit"
                      color="orange"
                      label="編集"
                      @click="editHighlight(highlight)"
                    />
                    <q-btn
                      flat
                      dense
                      size="sm"
                      icon="delete"
                      color="negative"
                      label="削除"
                      @click="deleteHighlight(highlight.id!)"
                    />
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </q-card-section>
        </q-card>
      </q-dialog>

      <!-- 動画情報 -->
      <div class="video-info q-mt-md">
        <q-card>
          <q-card-section>
            <div class="text-h6 q-mb-sm">動画情報</div>
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { api } from 'boot/axios';
import { SupabaseService } from 'src/services/supabaseService';
import { HighlightService, type Highlight } from 'src/services/highlightService';
import { Notify } from 'quasar';

interface RegisteredVideo {
  video_id: string;
  total_study_time: number;
  total_new_cards: number;
  total_learning_cards: number;
  total_review_cards: number;
  created_at: string;
}

interface SubtitleEntry {
  text: string;
  start: number;   // 秒
  duration: number; // 秒
}

const route = useRoute();
const registeredVideos = ref<RegisteredVideo[]>([]);
const isLoading = ref(false);
const selectedVideo = ref<RegisteredVideo | null>(null);

// 字幕関連の状態
const englishSubtitles = ref<SubtitleEntry[]>([]);
const japaneseSubtitles = ref<SubtitleEntry[]>([]);
const displaySubtitles = ref<SubtitleEntry[]>([]); // 表示用（今回は英語優先）
const currentTimeSec = ref<number>(0);
const playerIframe = ref<HTMLIFrameElement | null>(null);
let timeTicker: number | null = null;

// ハイライト関連の状態
const highlights = ref<Highlight[]>([]);
const showHighlightDialog = ref(false);
const showHighlightListDialog = ref(false);
const isGenerating = ref(false);
const isSaving = ref(false);
const generatedData = ref(false);
const imageFile = ref<File | null>(null);
const editingHighlightId = ref<number | null>(null);
const highlightForm = ref({
  highlighted_text: '',
  timestamp: 0,
  meaning_japanese: '',
  etymology: '',
  image_url: '',
  auto_generate: true,
});

const getRegisteredVideos = async (channelId?: string) => {
  isLoading.value = true;
  try {
    // Try Supabase first, fallback to API
    try {
      const supabaseVideos = await SupabaseService.getVideos();
      if (supabaseVideos.length > 0) {
        let filteredVideos = supabaseVideos;
        if (channelId) {
          filteredVideos = supabaseVideos.filter(video => video.channel_id === channelId);
        }
        registeredVideos.value = filteredVideos.map(video => ({
          video_id: video.video_id,
          total_study_time: video.total_study_time,
          total_new_cards: video.total_new_cards,
          total_learning_cards: video.total_learning_cards,
          total_review_cards: video.total_review_cards,
          created_at: video.created_at
        }));
        return;
      }
    } catch (supabaseError) {
      console.warn('Supabase not available, using API fallback:', supabaseError);
    }

    // API fallback
    const params = channelId ? { channel_id: channelId } : {};
    const response = await api.get('videos/', { params });
    if (response.status === 200) {
      registeredVideos.value = response.data;
    }
  } catch (error) {
    console.error('Error fetching registered videos:', error);
  } finally {
    isLoading.value = false;
  }
};

const loadSubtitles = async (videoId: string) => {
  try {
    const response = await api.get(`videos/${videoId}/transcript/`);
    const data = response.data;

    if (data.error) {
      console.warn('Subtitle API error:', data.error);
      englishSubtitles.value = [];
      japaneseSubtitles.value = [];
      displaySubtitles.value = [];
      return;
    }

    // 互換: data.english / data.japanese 形式 or Gemini整形済み形式どちらにも対応
    if (Array.isArray(data.english)) {
      englishSubtitles.value = data.english as SubtitleEntry[];
    } else if (data.subtitles?.english?.transcript) {
      englishSubtitles.value = data.subtitles.english.transcript as SubtitleEntry[];
    } else {
      englishSubtitles.value = [];
    }

    if (Array.isArray(data.japanese)) {
      japaneseSubtitles.value = data.japanese as SubtitleEntry[];
    } else if (data.subtitles?.japanese?.transcript) {
      japaneseSubtitles.value = data.subtitles.japanese.transcript as SubtitleEntry[];
    } else {
      japaneseSubtitles.value = [];
    }

    // 表示は英語優先、なければ日本語
    displaySubtitles.value = englishSubtitles.value.length ? englishSubtitles.value : japaneseSubtitles.value;
  } catch (e) {
    console.error('Failed to load subtitles:', e);
    englishSubtitles.value = [];
    japaneseSubtitles.value = [];
    displaySubtitles.value = [];
  }
};

const selectVideo = async (video: RegisteredVideo) => {
  selectedVideo.value = video;
  currentTimeSec.value = 0;
  await loadSubtitles(video.video_id);
  startTicker();
};

const startTicker = () => {
  if (timeTicker) {
    window.clearInterval(timeTicker);
  }
  // 簡易ティッカー（1秒ごと）。クリックシーク時に値を更新して整合を保つ
  timeTicker = window.setInterval(() => {
    currentTimeSec.value += 1;
  }, 1000);
};

const stopTicker = () => {
  if (timeTicker) {
    window.clearInterval(timeTicker);
    timeTicker = null;
  }
};

const isCurrentSubtitle = (sub: SubtitleEntry) => {
  const start = sub.start;
  const end = sub.start + (sub.duration || 0);
  // durationが0/未設定の場合は±1.5秒幅で判定
  if (!end || end <= start) {
    return Math.abs(currentTimeSec.value - start) <= 1.5;
  }
  return currentTimeSec.value >= start && currentTimeSec.value < end;
};

const formatTime = (sec: number) => {
  const m = Math.floor(sec / 60).toString().padStart(2, '0');
  const s = Math.floor(sec % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
};

const seekTo = (seconds: number) => {
  currentTimeSec.value = Math.max(0, Math.floor(seconds));
  // YouTube IFrame API への postMessage コマンド
  const iframeEl = playerIframe.value as HTMLIFrameElement | null;
  if (!iframeEl || !iframeEl.contentWindow) return;
  const message = JSON.stringify({
    event: 'command',
    func: 'seekTo',
    args: [currentTimeSec.value, true]
  });
  iframeEl.contentWindow.postMessage(message, '*');
};

const removeVideo = async (video: RegisteredVideo) => {
  try {
    // Try Supabase first
    let success = false;
    try {
      success = await SupabaseService.deleteVideo(video.video_id);
    } catch (supabaseError) {
      console.warn('Supabase delete failed, using API fallback:', supabaseError);
    }

    // API fallback if Supabase fails
    if (!success) {
      const response = await api.delete(`videos/${video.video_id}/`);
      success = response.status === 200;
    }

    if (success) {
      registeredVideos.value = registeredVideos.value.filter(v => v.video_id !== video.video_id);

      if (selectedVideo.value?.video_id === video.video_id) {
        stopTicker();
        selectedVideo.value = null;
      }
    }
  } catch (error) {
    console.error('Error removing video:', error);
    alert('動画の削除に失敗しました');
  }
};

// ハイライト関連の関数
const handleTextSelection = (event: MouseEvent, subtitle: SubtitleEntry) => {
  const selection = window.getSelection();
  const selectedText = selection?.toString().trim();

  if (!selectedText || selectedText.length === 0) {
    return; // 選択されていない場合は何もしない
  }

  // ダイアログを開く
  highlightForm.value = {
    highlighted_text: selectedText,
    timestamp: subtitle.start,
    meaning_japanese: '',
    etymology: '',
    auto_generate: true,
  };
  generatedData.value = false;
  showHighlightDialog.value = true;
};

const closeHighlightDialog = () => {
  showHighlightDialog.value = false;
  generatedData.value = false;
  editingHighlightId.value = null;
  imageFile.value = null;
  highlightForm.value = {
    highlighted_text: '',
    timestamp: 0,
    meaning_japanese: '',
    etymology: '',
    image_url: '',
    auto_generate: true,
  };
};

const saveHighlight = async () => {
  if (!selectedVideo.value) return;

  isSaving.value = true;
  try {
    if (editingHighlightId.value) {
      // 更新
      const updatedHighlight = await HighlightService.updateHighlight(
        editingHighlightId.value,
        {
          highlighted_text: highlightForm.value.highlighted_text,
          timestamp: highlightForm.value.timestamp,
          meaning_japanese: highlightForm.value.meaning_japanese,
          etymology: highlightForm.value.etymology,
          image_url: highlightForm.value.image_url,
        }
      );

      // リストを更新
      const index = highlights.value.findIndex(h => h.id === editingHighlightId.value);
      if (index !== -1) {
        highlights.value[index] = updatedHighlight;
      }

      Notify.create({
        type: 'positive',
        message: 'ハイライトを更新しました',
        position: 'top',
      });
    } else {
      // 新規作成
      const payload: any = {
        video_id: selectedVideo.value.video_id,
        highlighted_text: highlightForm.value.highlighted_text,
        timestamp: highlightForm.value.timestamp,
        auto_generate: highlightForm.value.auto_generate,
      };

      // 手動入力された値も送信
      if (highlightForm.value.meaning_japanese) {
        payload.meaning_japanese = highlightForm.value.meaning_japanese;
      }
      if (highlightForm.value.etymology) {
        payload.etymology = highlightForm.value.etymology;
      }
      if (highlightForm.value.image_url) {
        payload.image_url = highlightForm.value.image_url;
      }

      const newHighlight = await HighlightService.createHighlight(payload);

      // ハイライトリストに追加
      highlights.value.unshift(newHighlight);

      Notify.create({
        type: 'positive',
        message: 'ハイライトを保存しました',
        position: 'top',
      });
    }

    closeHighlightDialog();
  } catch (error) {
    console.error('Error saving highlight:', error);
    Notify.create({
      type: 'negative',
      message: 'ハイライトの保存に失敗しました',
      position: 'top',
    });
  } finally {
    isSaving.value = false;
  }
};

const deleteHighlight = async (highlightId: number) => {
  try {
    await HighlightService.deleteHighlight(highlightId);
    highlights.value = highlights.value.filter(h => h.id !== highlightId);

    Notify.create({
      type: 'positive',
      message: 'ハイライトを削除しました',
      position: 'top',
    });
  } catch (error) {
    console.error('Error deleting highlight:', error);
    Notify.create({
      type: 'negative',
      message: 'ハイライトの削除に失敗しました',
      position: 'top',
    });
  }
};

const loadHighlights = async (videoId: string) => {
  try {
    highlights.value = await HighlightService.getHighlights(videoId);
  } catch (error) {
    console.error('Error loading highlights:', error);
  }
};

// 画像アップロード処理
const handleImageUpload = async (file: File | null) => {
  if (!file) {
    highlightForm.value.image_url = '';
    return;
  }

  try {
    // 画像をBase64に変換（簡易実装）
    const reader = new FileReader();
    reader.onload = (e) => {
      highlightForm.value.image_url = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  } catch (error) {
    console.error('Error uploading image:', error);
    Notify.create({
      type: 'negative',
      message: '画像のアップロードに失敗しました',
      position: 'top',
    });
  }
};

// 画像削除
const removeImage = () => {
  highlightForm.value.image_url = '';
  imageFile.value = null;
};

// ハイライト編集
const editHighlight = (highlight: Highlight) => {
  editingHighlightId.value = highlight.id!;
  highlightForm.value = {
    highlighted_text: highlight.highlighted_text,
    timestamp: highlight.timestamp,
    meaning_japanese: highlight.meaning_japanese || '',
    etymology: highlight.etymology || '',
    image_url: highlight.image_url || '',
    auto_generate: false, // 編集時はAI生成オフ
  };
  showHighlightListDialog.value = false;
  showHighlightDialog.value = true;
};

// タイムスタンプへジャンプして一覧を閉じる
const seekToAndClose = (timestamp: number) => {
  seekTo(timestamp);
  showHighlightListDialog.value = false;
};

// 画像読み込みエラーハンドリング
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  console.error('Image failed to load:', img.src);
  // 画像が読み込めない場合は非表示にする
  img.style.display = 'none';
};

// 動画選択時にハイライトを読み込む
watch(selectedVideo, (newVideo) => {
  if (newVideo) {
    loadHighlights(newVideo.video_id);
  } else {
    highlights.value = [];
  }
});

onMounted(() => {
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

.video-player {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.subtitle-list .subtitle-scroll {
  max-height: 260px;
  overflow-y: auto;
}

.subtitle-row {
  display: flex;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  user-select: text; /* テキスト選択を有効化 */
}

.subtitle-row:hover { background: rgba(0,0,0,0.04); }
.subtitle-row .time { color: #607d8b; font-variant-numeric: tabular-nums; width: 48px; }
.subtitle-row .text {
  flex: 1;
  user-select: text; /* テキスト選択を有効化 */
  cursor: text; /* テキストカーソルを表示 */
}
.subtitle-row .text::selection {
  background-color: #ffeb3b; /* ハイライトカラー */
  color: #000;
}
.subtitle-row.is-current {
  background: linear-gradient(135deg, rgba(25,118,210,0.10), rgba(25,118,210,0.06));
  border-left: 3px solid #1976d2;
}

/* ハイライトリストのスタイル */
.highlights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.highlight-card {
  transition: transform 0.2s, box-shadow 0.2s;
  border-left: 3px solid #4caf50;
}

.highlight-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.highlight-image {
  width: 100%;
  max-height: 150px;
  object-fit: cover;
  border-radius: 4px;
  display: block;
}

.ellipsis-2-lines {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ellipsis-3-lines {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>