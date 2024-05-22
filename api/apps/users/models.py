from django.db import models

# Create your models here.
class UserInfo(models.Model):
  user_id = models.CharField(max_length=100, primary_key=True)
  user_name = models.CharField(max_length=15,verbose_name="ユーザー名")
  user_icon = models.ImageField(upload_to="icons/", verbose_name="ユーザーアイコン")
  created_at = models.DateField()

class Meta:
  db_table = "users"
  verbose_name = "ユーザー情報"
  
  def __str__(self):
    return self.use_name