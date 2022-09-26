from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, Client

from posts.models import Post, Group


User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='StasBasov')
        cls.user = User.objects.create_user(username='NoName')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user_author,
        )
        Post.objects.create(
            text='Пост для подписчиков',
            author=cls.user
        )
        Post.objects.create(
            text='Пост для подписчиков',
            author=cls.user
        )
        cls.group = Group.objects.create(
            title='Leo',
            slug='leo',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_url_and_their_names(self):
        urls_names = [
            (f'/profile/{self.user.username}/',
             reverse(
                 'posts:profile',
                 kwargs={'username': self.user.username}
             )),
            ('/', reverse('posts:index')),
            (f'/group/{self.group.slug}/',
             reverse(
                 'posts:group_list',
                 kwargs={'slug': self.group.slug}
             )),
            (f'/posts/{self.post.id}/',
             reverse(
                 'posts:post_detail',
                 kwargs={'post_id': self.post.id}
             )),
            (f'/posts/{self.post.id}/edit/',
             reverse(
                 'posts:post_edit',
                 kwargs={'post_id': self.post.id}
             )),
            ('/create/', reverse('posts:post_create')),
            ('/create/group/', reverse('posts:group_create')),
        ]
        for tuple in urls_names:
            address, reverse_name = tuple
            with self.subTest(address=address):
                self.assertEqual(address, reverse_name)

    def test_urls(self):
        """Проверка URL при открытии их пользователем"""
        equal_urls_name = [
            (reverse('posts:index'),
             HTTPStatus.OK,
             False,
             'Главная траница не доступна'),
            (reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}),
             HTTPStatus.OK,
             False,
             'Главная страница группы не доступна'),
            (reverse(
                'posts:profile',
                kwargs={'username': self.user.username}),
             HTTPStatus.OK,
             False,
             'Профиль пользователя не доступен'),
            (reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}),
             HTTPStatus.OK,
             False,
             'Подробная информация поста не доступна'),
            ('/unexisting_page/',
             HTTPStatus.NOT_FOUND,
             False,
             'Эта страница почему то доступна'),
            (reverse('posts:post_create'),
             HTTPStatus.OK,
             True,
             ('После открытия страницы создания поста авторизованным '
              'пользователем нет редиректа')),
            (reverse('posts:group_create'),
             HTTPStatus.OK,
             True,
             ('После открытия страницы создания группы авторизованным'
              'пользователем нет редиректа')),
            (reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}),
             HTTPStatus.OK,
             True,
             ('После изменения поста авторизованным пользователем '
              'нет редиректа')),
        ]
        for tuple in equal_urls_name:
            address, expected, auth, comment = tuple
            with self.subTest(address=address):
                if auth:
                    response = self.authorized_client.get(address)
                else:
                    response = self.guest_client.get(address)
                self.assertEqual(response.status_code, expected, comment)

    def test_url_redirect_for_unauthorized(self):
        redirects_urls = [
            (reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}),
                f'/auth/login/?next=/posts/{self.post.id}/edit/'),

            (reverse('posts:group_create'),
                '/auth/login/?next=/create/group/'),

            (reverse('posts:post_create'),
                '/auth/login/?next=/create/'),

            (reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
                f'/auth/login/?next=/posts/{self.post.id}/comment/'),

            (reverse('posts:profile_follow',
                     kwargs={'username': self.user.username}),
             f'/auth/login/?next=/profile/{self.user.username}/follow/'),

            (reverse('posts:profile_unfollow',
                     kwargs={'username': self.user.username}),
             f'/auth/login/?next=/profile/{self.user.username}/unfollow/')
        ]
        for tuple in redirects_urls:
            address, expected = tuple
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertRedirects(response, expected)

    def test_post_edit_authorized_not_author(self):
        """Проверка редактирования поста пользователем,
           который не является автором"""
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))

    def test_templates(self):
        """Проверка вывода правильных шаблонов для каждого URL"""
        templates_urls_names = {
            (reverse('posts:index'), 'posts/index.html'),
            (reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}), 'posts/group_list.html'),
            (reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ), 'posts/profile.html'),
            (reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}), 'posts/post_detail.html'),
            (reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}), 'posts/post_create.html'),
            (reverse('posts:post_create'), 'posts/post_create.html'),
            (reverse('posts:group_create'), 'posts/group_create.html'),
        }
        for tuple in templates_urls_names:
            address, template = tuple
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
