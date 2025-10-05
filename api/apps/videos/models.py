from django.db import models

# Create your models here.
class Videos(models.Model):
  video_id = models.CharField(verbose_name='ビデオID', max_length=100, unique=True, primary_key=True)
  channel_id = models.CharField(verbose_name='チャンネルID', max_length=100, default='unknown')
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