from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus
from urllib.parse import urljoin

from django.contrib.auth import get_user_model

from posts.models import Post, Group

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_name1',
                                            email='test@mail.ru',
                                            password='test_pass'),
            text='Тестовая запись для создания нового поста',)

        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test_slug'
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.user = User.objects.create_user(username='mob2556')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/test_name1/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_exists_at_desired_location(self):
        """Страница по адресу использует шаблон, доступ любому пользователю"""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/test_name1/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_task_list_url_exists_at_desired_location(self):
        """Проверяем доступность страниц для авторизованного пользователя"""
        templates_url_names = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/test_name1/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_author_username_edit_post_url(self):
        """
        Проверка доступности страницы редактирования поста, при обращении
        автора
        """
        list_of_available_id = Post.objects.filter(
            author=self.user).values_list('id', flat=True)
        for available_id in list_of_available_id:
            with self.subTest(available_id=available_id):
                url = reverse('post_edit', args=[self.author, available_id])
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(
                    self.authorized_client.get(
                        f'{self.user.username}/{available_id}/edit/'),
                    'posts/create_post.html'
                )

    def test_redirect_anon_username_edit_post_url(self):
        """
        Проверка редиректа анонимного пользователя, при обращении
        к странице редактирования поста
        """
        response = self.guest_client.get('/posts/1/edit/')
        url = urljoin(reverse('login'), "?next=/posts/1/edit/")
        self.assertRedirects(response, url)

    def test_redirect_non_author_username_edit_post_url(self):
        """Проверка редиректа авторизованного пользователя не автора,
        при обращении к странице редактирования поста"""
        response = self.guest_client.get('/posts/1/edit/')
        url = urljoin(reverse('login'), "?next=/posts/1/edit/")
        self.assertRedirects(response, url)

    def test_page_404(self):
        """Проверка на ошибку 404 при неизвестном клиенте"""
        response = self.guest_client.get('/qwerty12345/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
