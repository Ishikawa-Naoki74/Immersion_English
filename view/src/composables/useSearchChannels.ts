import { ref } from 'vue';
import { api } from 'boot/axios';
import { useChannelsStore } from 'stores/channels-store';
import { useRouter } from 'vue-router';

export function useSearchChannels() {
  const searchQuery = ref<string>('');
  const channelsStore = useChannelsStore();
  const router = useRouter();

  const searchChannels = async (event?: Event) => {
    try {
      const response = await api.get('youtube/channels', {
        params: { search_query: searchQuery.value }
      });
      channelsStore.setChannels (response.data);
      router.push({ name: 'search-channels-result' })
    } catch (error) {
      console.error('Error search channels', error);
    }
  };
  return {
    searchQuery,
    searchChannels
  }
}
