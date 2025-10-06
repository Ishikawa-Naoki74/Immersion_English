from rest_framework import serializers
from .models import Videos, Highlight
from apps.channel_decks.serializers import ChannelDecksSerializer

class VideosSerializer(serializers.ModelSerializer):
    channel_info = ChannelDecksSerializer(source='channel', read_only=True)
    channel_id = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Videos
        fields = ['video_id', 'channel_id', 'channel_info', 'total_study_time',
                  'total_new_cards', 'total_learning_cards', 'total_review_cards', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # channel_idを追加
        if instance.channel:
            representation['channel_id'] = instance.channel.channel_id
        return representation


class HighlightSerializer(serializers.ModelSerializer):
    video_id = serializers.CharField(write_only=True)

    class Meta:
        model = Highlight
        fields = ['id', 'video_id', 'highlighted_text', 'timestamp',
                  'meaning_japanese', 'etymology', 'image_url',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['video_id'] = instance.video.video_id
        return representation