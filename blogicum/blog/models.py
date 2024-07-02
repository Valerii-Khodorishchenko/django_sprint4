from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone


User = get_user_model()


class PublicationModel(models.Model):
    is_published = models.BooleanField(
        verbose_name='Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(verbose_name='Добавлено',
                                      auto_now_add=True)

    class Meta:
        abstract = True


class Category(PublicationModel):
    title = models.CharField(verbose_name='Заголовок', max_length=256)
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        verbose_name='Идентификатор',
        help_text=('Идентификатор страницы для URL; разрешены символы '
                   'латиницы, цифры, дефис и подчёркивание.'),
        unique=True
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:20] + '...'


class Location(PublicationModel):
    name = models.CharField(verbose_name='Название места', max_length=256)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:20] + '...'


class Post(PublicationModel):
    title = models.CharField(verbose_name='Заголовок', max_length=256)
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=('Если установить дату и время в будущем — можно делать '
                   'отложенные публикации.'),
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        on_delete=models.CASCADE,
    )
    location = models.ForeignKey(
        Location,
        verbose_name='Местоположение',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts_at_location',
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True,
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts_images',
        blank=True
    )

    class Meta:
        default_related_name = 'posts'
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date', 'title')

    def __str__(self):
        return f'Пост: {self.title[:20]}... |Текст: {self.text[:40]}...'


class Comments(models.Model):
    text = models.TextField(verbose_name='Коментарий')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Оставлен')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )

    class Meta:
        default_related_name = 'comments'
        verbose_name = 'Коментарий'
        verbose_name_plural = 'Коментарии'
        ordering = ('created_at',)

    def __str__(self):
        return self.text[20] + '...'


def category_check(slug):
    return get_object_or_404(
        Category,
        slug=slug,
        is_published=True,
    )


def filter_published(queryset):
    return queryset.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )


def get_posts(posts):
    return posts.select_related(
        'location',
        'author',
        'category'
    ).annotate(
        comment_count=Count('comments')
    ).order_by(
        '-pub_date',
    )
