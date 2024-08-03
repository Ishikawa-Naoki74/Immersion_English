import { ref, computed } from 'vue';
import { useRoute } from 'vue-router';
import { Video } from '../types/video';
import { fetchChannelVideos } from '../services/youtubeService';
import { usePageTokens } from './usePageTokens';
import { enhanceVideo } from '../helpers/videoHelpers';

export function useChannelVideos() {
  const route = useRoute();
  const videos = ref<(Video & { isPlaying: boolean })[]>([]);
  const totalVideos = ref(0);
  const currentPage = ref(1);
  const perPage = 50;
  const isLoading = ref(false);

  // usePageTokens をここで呼び出さずに、getChannelVideos 内で使用する
  const pageTokensMap = new Map<string, ReturnType<typeof usePageTokens>>();

  const totalPages = computed(() => Math.ceil(totalVideos.value / perPage));

  const getChannelVideos = async (page: number) => {
    const uploadsPlaylistId = route.query.playlist_id as string;
    if (!uploadsPlaylistId) {
      console.error('playlist_id is missing');
      return;
    }

    // プレイリストIDごとに usePageTokens のインスタンスを管理
    if (!pageTokensMap.has(uploadsPlaylistId)) {
      pageTokensMap.set(uploadsPlaylistId, usePageTokens(uploadsPlaylistId));
    }
    const { getPageToken, addPageToken } = pageTokensMap.get(uploadsPlaylistId)!;

    isLoading.value = true;
    try {
      const pageToken = await getPageToken(page);
      const response = await fetchChannelVideos(uploadsPlaylistId, pageToken, perPage);
      videos.value = response.videos.map(enhanceVideo);
      totalVideos.value = response.totalResults;

      if (response.nextPageToken) {
        addPageToken(page + 1, response.nextPageToken);
      }
    } catch (error) {
      console.error('Error fetching channel videos:', error);
    } finally {
      isLoading.value = false;
    }
  };

  const playVideo = (video: Video & { isPlaying: boolean }) => {
    video.isPlaying = true;
  };

  return {
    videos,
    totalVideos,
    currentPage,
    totalPages,
    isLoading,
    getChannelVideos,
    playVideo,
  };
}
