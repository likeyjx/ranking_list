from django.db import models

# Create your models here.
class UserProfile(models.Model):

    username = models.CharField(max_length=11,verbose_name='用户昵称')
    password = models.CharField(max_length=20,verbose_name='密码')