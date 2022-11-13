from django.db import models
from django.contrib.auth import get_user_model
# Нужно установить библиотеку pytils:
# pip3 install pytils from pytils.translit import slugify

User = get_user_model()


class Group(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name='group_name')
    slug = models.SlugField(
        null=True,
        unique=True,
        max_length=200,
    )
    description = models.TextField(verbose_name='group_descrittion')

    def __str__(self) -> str:
        return self.title

    # Расширение встроенного метода save(): если поле slug не заполнено -
    # транслитерировать в латиницу содержимое поля title, обрез. до ста знаков
    # и сохранить в поле slug
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = (self.title)[:100]
        super().save(*args, **kwargs)


class Post(models.Model):
    text = models.TextField(
        verbose_name='post_text',
        help_text='Текст поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата',
        # db_index=True
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        verbose_name='Группа',
        related_name='posts',
        on_delete=models.SET_NULL,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Пользователь'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
        help_text='Под каким постом оставлен комментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
        help_text='Автор отображается на сайте'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Обязательное поле, не должно быть пустым'
    )
    created = models.DateTimeField(
        verbose_name='Дата публикации',
        help_text='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-created',)
        verbose_name_plural = 'Комментарии к постам'

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")
