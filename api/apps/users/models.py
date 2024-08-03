from django.db import models

# Create your models here.
class Users(models.Model):
  user_id = models.CharField(verbose_name='firebaseUID', max_length=100, unique=True, primary_key=True)
  user_name = models.CharField(verbose_name="ユーザー名", max_length=15, blank=True, null=True)
  user_icon = models.ImageField(verbose_name="ユーザーアイコン", upload_to="icons/", blank=True, null=True)
  created_at = models.DateTimeField(verbose_name="作成日時", auto_now_add=True)

  class Meta:
    db_table = "users"
    verbose_name = "ユーザー情報"
  
  def __str__(self):
    return self.use_name