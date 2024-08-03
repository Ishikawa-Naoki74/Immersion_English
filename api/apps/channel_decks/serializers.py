from rest_framework import serializers
from .models import Channeldecks

class ChannelDecksSerializer(serializers.ModelSerializer):
  class Meta:
    model = Channeldecks
    fields = '__all__'
