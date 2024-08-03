from django.db import models
import uuid
# Create your models here.
class Channeldecks(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  channel_id = models.CharField(verbose_name='チャンネルID', max_length=100, unique=True)
  channel_title = models.CharField(verbose_name='チャンネル名', max_length=100)
  channel_icon_url = models.URLField(verbose_name='チャンネルアイコン', max_length=200)
  total_study_time = models.IntegerField(verbose_name='学習時間', default=0)
  total_new_cards = models.IntegerField(verbose_name='新規', default=0)
  total_learning_cards = models.IntegerField(verbose_name='習得中', default=0)
  total_review_cards = models.IntegerField(verbose_name='復習', default=0, blank=True)
  uploads_playlist_id = models.CharField(verbose_name='プレイリストID', max_length=100)
  created_at = models.DateTimeField(auto_now_add = True)

  class Meta:
    db_table = "channel_decks"
    verbose_name = "チャンネルデッキ"
    
  def __str__(self):
    return self.channel_icon_url