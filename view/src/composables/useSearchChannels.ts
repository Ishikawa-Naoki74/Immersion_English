import { ref } from 'vue';
import { searchChannels as searchChannelsAPI } from 'src/services/youtubeService';
import { useChannelsStore } from 'stores/channels-store';
import { useRouter } from 'vue-router';

export function useSearchChannels() {
  const searchQuery = ref<string>('');
  const channelsStore = useChannelsStore();
  const router = useRouter();

  const searchChannels = async (event?: Event) => {
    if (!searchQuery.value.trim()) {
      return;
    }
    
    try {
      const data = await searchChannelsAPI(searchQuery.value);
      
      if (data && Array.isArray(data)) {
        channelsStore.setChannels(data);
        router.push({ name: 'search-channels-result' });
      } else {
        console.error('Invalid response format:', data);
      }
    } catch (error: any) {
      console.error('Error search channels:', error);
      if (error.response) {
        console.error('Response status:', error.response.status);
        console.error('Response data:', error.response.data);
        console.error('Response headers:', error.response.headers);
        console.error('Request URL:', error.config?.url);
        console.error('Request params:', error.config?.params);
      } else if (error.request) {
        console.error('No response received:', error.request);
        console.error('Request URL:', error.config?.url);
        console.error('Request params:', error.config?.params);
      } else {
        console.error('Error message:', error.message);
      }
    }
  };
  return {
    searchQuery,
    searchChannels
  }
}
