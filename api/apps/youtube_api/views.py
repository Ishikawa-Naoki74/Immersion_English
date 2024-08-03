from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.youtube_service import YoutubeService

# channel search view
class ChannelSearchView(APIView):
  def get(self, request):
    search_query = request.GET.get('search_query', '')
    service = YoutubeService()
    channel_details = service.search_channels(search_query)
    
    return Response(channel_details)
  
# channel video view
class ChannelVideosView(APIView):
  def get(self, request):
    service = YoutubeService()
    playlist_id = request.GET.get('playlist_id', '')
    page_token = request.GET.get('page_token')
    per_page = int(request.GET.get('per_page', 50))
    channel_videos = service.get_channel_videos(playlist_id, page_token, per_page)

    return Response({
      'videos': channel_videos['videos'],
      'next_page_token': channel_videos['next_page_token'],
      'total_results': channel_videos['total_results']
    })
