from django.test import TestCase

from django.contrib.auth import get_user_model

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверка, что у моделей правильные имена"""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        group = PostModelTest.group
        expected_group_name = group.title
        self.assertEqual(expected_object_name, str(post))
        self.assertEqual(expected_group_name, str(group))

    def test_title_label(self):
        """verbose_name поля title совпадает с ожидаемым."""
        verboses = {
            'text': 'post_text',
            'pub_date': 'Дата',
            'group': 'Группа',
            'author': 'Пользователь',
            'image': 'Картинка',
        }
        for field, verbose in verboses.items():
            with self.subTest(verbose=verbose):
                post = PostModelTest.post
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, verbose)

    def test_title_help_text(self):
        """help_text поля title совпадает с ожидаемым."""
        post = PostModelTest.post
        help_text = post._meta.get_field('text').help_text
        self.assertEqual(help_text, 'Текст поста')
