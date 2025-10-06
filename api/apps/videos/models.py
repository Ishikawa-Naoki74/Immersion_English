from django.db import models
from apps.channel_decks.models import Channeldecks

# Create your models here.
class Videos(models.Model):
  video_id = models.CharField(verbose_name='ビデオID', max_length=100, unique=True, primary_key=True)
  channel = models.ForeignKey(
    Channeldecks,
    on_delete=models.CASCADE,
    to_field='channel_id',
    db_column='channel_id',
    verbose_name='チャンネル',
    related_name='videos',
    null=True,
    blank=True
  )
  total_study_time = models.IntegerField(default=0)
  total_new_cards = models.IntegerField(default=0)
  total_learning_cards = models.IntegerField(default=0)
  total_review_cards = models.IntegerField(default=0)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    db_table = "videos"
    verbose_name = "ビデオ"

  def __str__(self):
    return self.video_id


class Highlight(models.Model):
  """字幕でハイライトした部分を保存するモデル"""
  id = models.AutoField(primary_key=True)
  video = models.ForeignKey(
    Videos,
    on_delete=models.CASCADE,
    to_field='video_id',
    db_column='video_id',
    verbose_name='ビデオ',
    related_name='highlights'
  )
  highlighted_text = models.TextField(verbose_name='ハイライトした部分')
  timestamp = models.FloatField(verbose_name='タイムスタンプ（秒）', help_text='字幕の開始時間')
  meaning_japanese = models.TextField(verbose_name='日本語の意味', blank=True, null=True)
  etymology = models.TextField(verbose_name='語源', blank=True, null=True)
  image_url = models.URLField(verbose_name='イメージ画像URL', max_length=500, blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
  updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

  class Meta:
    db_table = "highlights"
    verbose_name = "ハイライト"
    verbose_name_plural = "ハイライト"
    ordering = ['-created_at']

  def __str__(self):
    return f"{self.video_id} - {self.highlighted_text[:50]}"
