from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count
from django.utils import timezone


User = get_user_model()


class PostQuerySet(models.QuerySet):

    def filter_published(self):
        return self.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )

    def filter_by_author(self, author):
        return self.filter(author=author)

    def get_posts(self):
        return (
            self.select_related('location', 'author', 'category')
            .order_by('-pub_date', 'title')
            .annotate(comment_count=Count('comments'))
        )


class PostManager(models.Manager):
    def get_user_post_cards(self, author):
        return PostQuerySet(self.model).get_posts().filter_by_author(author)

    def get_other_user_post_cards(self, author):
        return (
            PostQuerySet(self.model)
            .get_posts()
            .filter_by_author(author)
            .filter_published()
        )

    def get_published_posts(self):
        return PostQuerySet(self.model).get_posts().filter_published()


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
        return self.title


class Location(PublicationModel):
    name = models.CharField(verbose_name='Название места', max_length=256)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return f'{self.name[:20]}...'


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
        related_name='posts',
    )
    location = models.ForeignKey(
        Location,
        verbose_name='Местоположение',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts_images',
        blank=True
    )
    objects = PostQuerySet.as_manager()
    posts_objects = PostManager()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date', 'title')

    def __str__(self):
        return f'|Пост: {self.title[:20]}...\n|Текст: {self.text[:40]}...'


class Comments(models.Model):
    text = models.TextField('Введите коментарий')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)
