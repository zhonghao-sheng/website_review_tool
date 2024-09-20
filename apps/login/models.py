from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(models.Model):
    username = models.CharField('Username', max_length=50)
    password = models.CharField('Password', max_length=16)
# class User(AbstractUser):
#     username = models.CharField('Username', max_length=50, unique=True)
#     password = models.CharField('Password', max_length=16)
#     # email = models.CharField('Email', max_length=50, unique=True)
#     class Meta:
#         db_table = 'webtool_users'
#         verbose_name = 'user_management'
#         verbose_name_plural = verbose_name
#     def __str__(self):
#         return self.username