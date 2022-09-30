from django.db import models
from django.contrib.auth import get_user_model

from core.models import CreateModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Название",
        help_text="Укажите название группы"
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Ссылка на группу',
        help_text='Адрес вашей группы:',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание:',
        help_text='Опишите вашу группу:'
    )

    def __str__(self):
        return self.title


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подпысчик'
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='check_user'
            )
        ]


class Post(CreateModel):
    FIRST_FIFTEEN_SIMBOLS = 15
    text = models.TextField(
        verbose_name='Что у вас нового?',
        help_text='Введите текст:',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Имя пользователя',
        help_text='Выберите пользователя'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Название группы',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        verbose_name='картинка',
        help_text='Загрузите картинку',
        upload_to='posts/',
        blank=True,
        null=True,
    )

    class Meta(CreateModel.Meta):
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:self.FIRST_FIFTEEN_SIMBOLS]


class Comment(CreateModel):
    text = models.TextField(
        'Комментарий',
        max_length=400
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
        related_name='comments'
    )
    post = models.ForeignKey(
        Post,
        related_name='comments',
        verbose_name='Пост к которому отнсится комментарий',
        on_delete=models.CASCADE
    )

    class Meta(CreateModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Коментарии'
