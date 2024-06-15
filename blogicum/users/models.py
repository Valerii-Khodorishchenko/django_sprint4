from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    image = models.ImageField(
        'Фото',
        upload_to='user_images',
        blank=True
    )
    info = models.TextField(
        verbose_name='О пользователе',
        null=True,
        blank=True
    )
