import { ref } from 'vue';
import { fetchNextPageToken } from 'src/services/youtubeService';

export function usePageTokens(playlistId: string) {
  const pageTokens = ref<{ [key: number]: string | null }>({ 1: null });

  const addPageToken = (page: number, token: string) => {
    pageTokens.value[page] = token;
  };

  const getPageToken = async (targetPage: number): Promise<string | null> => {
    if (pageTokens.value[targetPage]) {
      return pageTokens.value[targetPage];
    }

    let currentPage = Object.keys(pageTokens.value).length;
    let currentToken = pageTokens.value[currentPage];

    while (currentPage < targetPage) {
      // この部分は実際のAPI呼び出しに置き換える必要があります
      const nextToken = await fetchNextPageToken(playlistId, currentToken);
      if (!nextToken) break;

      currentPage++;
      addPageToken(currentPage, nextToken);
      currentToken = nextToken;
    }

    return pageTokens.value[targetPage] || null;
  };

  return { pageTokens, addPageToken, getPageToken }
}
