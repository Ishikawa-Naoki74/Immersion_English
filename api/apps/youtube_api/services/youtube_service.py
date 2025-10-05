from googleapiclient import discovery
from googleapiclient import errors
from django.core.paginator import Paginator
from config.settings.base import YOUTUBE_DATA_API_KEY

class YoutubeService:
  def __init__(self):
    self.youtube = discovery.build('youtube', 'v3', developerKey = YOUTUBE_DATA_API_KEY)
  
  # get channel ids
  def get_channel_ids(self, search_query, max_result=10):
    try:
      channel_ids_request = self.youtube.search().list(
        q=search_query,
        type='channel',
        part='snippet',
        maxResults = max_result
      )
      response = channel_ids_request.execute()
      return [item['id']['channelId'] for item in response.get('items', [])]
    except errors.HttpError as e:
      print(f"YouTube API error in get_channel_ids: {e}")
      return []
    except Exception as e:
      print(f"General error in get_channel_ids: {e}")
      return []

  # get channel info
  def get_channel_details(self, channel_ids):
    try:
      if not channel_ids:
        return []
      
      if isinstance(channel_ids, list):
        channel_ids = ','.join(channel_ids)
      
      channel_details_request = self.youtube.channels().list(
        part='snippet,statistics,contentDetails',
        id=channel_ids
      )
      response = channel_details_request.execute()
      return [
        {
          'id': item['id'],
          'title': item['snippet']['title'],
          'thumbnail': item['snippet']['thumbnails']['default']['url'],
          'subscriberCount': item['statistics']['subscriberCount'],  
          'playlistId': item['contentDetails']['relatedPlaylists']['uploads']
        }
        for item in response.get('items', [])
      ]
    except errors.HttpError as e:
      print(f"YouTube API error in get_channel_details: {e}")
      return []
    except Exception as e:
      print(f"General error in get_channel_details: {e}")
      return []
  
  # search channels
  def search_channels(self, search_query, max_result=10):
    try:
      if not search_query.strip():
        return []
      
      channel_ids = self.get_channel_ids(search_query, max_result)
      if not channel_ids:
        return []
      
      channel_details = self.get_channel_details(channel_ids)
      return channel_details
    except errors.HttpError as e:
      print(f"YouTube API error in search_channels: {e}")
      return []
    except Exception as e:
      print(f"General error in search_channels: {e}")
      return []  
  
  # get channel videos
  def get_channel_videos(self, playlist_id, page_token=None, per_page=50):
        try:
           playlist_items_request = self.youtube.playlistItems().list(
           part='snippet',
           playlistId=playlist_id,
           maxResults=per_page,
           pageToken=page_token
           )
           response = playlist_items_request.execute()
           videos = [{
              'id': item['snippet']['resourceId']['videoId'],
              'title': item['snippet']['title'],
              'thumbnail': item['snippet']['thumbnails']['default']['url'],
              'published_at': item['snippet']['publishedAt']
              } for item in response.get('items', [])]

           return {
              'videos': videos,
              'next_page_token': response.get('nextPageToken'),
              'total_results': response['pageInfo']['totalResults'],
              }
        
        except errors.HttpError as e:
          print(f"An error occurred: {e}")
          return None