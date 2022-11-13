from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class TestCreateForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Группа Игоря',
            slug='test_slug',
            description='Группу создал Игорь',
        )

        cls.author = User.objects.create_user(
            username='author_post',
            first_name='Тест',
            last_name='Теcта',
            email='test@yatube.ru'
        )

        cls.post = Post.objects.create(
            group=TestCreateForm.group,
            text="Какой-то там текст",
            author=User.objects.get(username='author_post'),
        )

        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestForTest')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorised_new_post(self): 
        """Проверка создания нового поста, авторизированным пользователем""" 
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')
        form_data = { 
            'group': self.group.id, 
            'text': 'Пост от авторизованного пользователя',
            'image': uploaded 
        }
        response = self.authorized_client.post( 
            reverse('posts:create_post'), 
            data=form_data, 
            follow=True) 
        new_post = Post.objects.first() 
        self.assertEqual(new_post.group, self.group) 
        self.assertEqual(new_post.author, self.user) 
        self.assertRedirects( 
            response, 
            reverse('posts:profile', args=['TestForTest'])) 
        self.assertEqual(Post.objects.count(), post_count + 1) 
        self.assertTrue(Post.objects.filter( 
            text='Пост от авторизованного пользователя', 
            group=TestCreateForm.group).exists()) 

    def test_guest_new_post(self):
        """Неавторизоанный не может создавать посты"""
        form_data = {
            'group': self.group.id,
            'text': 'Пост от неавторизованного пользователя',
        }
        self.guest_client.post(
            reverse('posts:create_post'),
            data=form_data,
            follow=True,
        )
        self.assertFalse(Post.objects.filter(
            text='Пост от неавторизованного пользователя').exists())

    def test_form_update(self):
        """Проверка редактирования поста через форму на странице"""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        url = reverse('posts:post_edit', args=[1])
        self.authorized_client.get(url)
        self.new_group = Group.objects.create(
            title='Новая группа Игоря',
            slug='test_slug_2',
            description='Группу создал Игорь',
        )
        form_data = {
            'group': self.new_group.id,
            'text': 'Обновленный текст',
        }
        self.authorized_client.post(
            reverse('posts:post_edit', args=[1]),
            data=form_data, follow=True
        )
        self.assertTrue(Post.objects.filter(
            text='Обновленный текст',
            group=self.new_group).exists()
        )
        old_group_response = self.authorized_client.get(
            reverse('posts:group_list', args=(self.group.slug,)))
        self.assertEqual(
            old_group_response.context['page_obj'].paginator.count, 0)
