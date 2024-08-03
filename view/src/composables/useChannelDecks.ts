import { ref } from 'vue';
import { api } from 'boot/axios';
import { ChannelDeck } from '../types/channelDeck';

export function useChannelDecks() {
  const channelDecks = ref<ChannelDeck[]>([]);

  const getChannelDecks = async () => {
    try {
      const response = await api.get('channels');
      if (response.status === 200 && response.data) {
        channelDecks.value = response.data;
      } else {
        console.log('Failed to get channel decks')
      }
    } catch (error) {
      console.error('Error getting channel decks', error);
    }
  };

  return {
    channelDecks,
    getChannelDecks
  }
}
