import { api } from 'boot/axios';

export async function fetchChannelVideos(playlistId: string, pageToken: string | null, perPage: number) {
  const response = await api.get('youtube/videos/', {
    params: {
      playlist_id: playlistId,
      page_token: pageToken,
      per_page: perPage
    }
  });

  if (response.status !== 200 || !response.data) {
    throw new Error('Failed to fetch videos');
  }

  return {
    videos: response.data.videos,
    totalResults: response.data.total_results,
    nextPageToken: response.data.next_page_token
  };
}

export async function fetchNextPageToken(playlistId: string, currentToken: string | null): Promise<string | null> {
  try {
    const response = await api.get('youtube/videos/', {
      params: {
        playlist_id: playlistId,
        page_token: currentToken,
        per_page: 1  // 次のページトークンだけが必要なので、最小限のデータを要求
      }
    });

    if (response.status === 200 && response.data) {
      return response.data.next_page_token || null;
    } else {
      console.error('Failed to fetch next page token');
      return null;
    }
  } catch (error) {
    console.error('Error fetching next page token:', error);
    return null;
  }
}

export async function searchChannels(searchQuery: string) {
  try {
    console.log('Searching channels with query:', searchQuery);
    console.log('API base URL:', api.defaults.baseURL);
    
    const response = await api.get('youtube/channels/', {
      params: {
        search_query: searchQuery
      }
    });

    console.log('Response status:', response.status);
    console.log('Response data:', response.data);

    if (response.status !== 200 || !response.data) {
      throw new Error('Failed to search channels');
    }

    return response.data;
  } catch (error: any) {
    console.error('Error searching channels:', error);
    if (error.response) {
      console.error('Error response status:', error.response.status);
      console.error('Error response data:', error.response.data);
      console.error('Error response headers:', error.response.headers);
    } else if (error.request) {
      console.error('No response received');
      console.error('Request:', error.request);
    } else {
      console.error('Error message:', error.message);
    }
    console.error('Request URL:', error.config?.url);
    console.error('Request method:', error.config?.method);
    console.error('Request params:', error.config?.params);
    throw error;
  }
}
