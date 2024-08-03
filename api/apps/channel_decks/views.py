from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Channeldecks
from .serializers import ChannelDecksSerializer
class ChannelDecksView(APIView):
 # TODO serializerでデシリアライズする
  def post(self, request):
    channel_id = request.data.get('channel_id')
    channel_icon_url = request.data.get('channel_icon_url')
    channel_title = request.data.get('channel_title')
    uploads_playlist_id = request.data.get('uploads_playlist_id')

    if Channeldecks.objects.filter(channel_id=channel_id).exists():
      return Response({'message': 'Channel already registered'}, status = status.HTTP_200_OK)
    channel_deck = Channeldecks(channel_id=channel_id, channel_title=channel_title, channel_icon_url=channel_icon_url, uploads_playlist_id=uploads_playlist_id)
    channel_deck.save()
    return Response({'message': 'Channel registered successfully'}, status = status.HTTP_201_CREATED)
  
  def get(self, request):
    channelDecks = Channeldecks.objects.all()
    serializer = ChannelDecksSerializer(channelDecks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
  
  def delete(self, request, channel_id, format=None):
     try:
      channelDeck = Channeldecks.objects.get(channel_id=channel_id)
      channelDeck.delete()
      return Response({'message': 'Channel deleted successfully'}, status=status.HTTP_200_OK)
     except Channeldecks.DoesNotExist:
      return Response({'message': 'Channel not found'}, status=status.HTTP_404_NOT_FOUND)
     except Exception as e:
       return Response({'message': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)