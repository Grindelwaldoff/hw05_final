import math
from itertools import islice

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.conf import settings
from django.core.cache import cache
from django.urls import reverse

from posts.models import User, Group, Post, Follow
from posts.forms import PostForm


User = get_user_model()


class ViewURLTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasBasov')
        cls.follower = User.objects.create_user(username='Folower')
        cls.group = Group.objects.create(
            title='Leo',
            slug='leo',
        )
        cls.not_related_group = Group.objects.create(
            title='Leonid',
            slug='leonid',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )
        cls.post_follower = Post.objects.create(
            text='Тестовый пост подписчика',
            author=cls.follower,
            group=cls.group,
        )
        Follow.objects.create(
            user=cls.user,
            author=cls.follower
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_group_list_right_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.not_related_group.slug}
            )
        )
        self.assertNotIn(
            response.context['page_obj'],
            Post.objects.filter(id=self.post.id),
        )

    def test_folow_index_context(self):
        """Проверка что посты автора не появляются у тех,
            кто на него не подписан"""
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            len(response.context['page_obj']),
            1
        )
        """Проверка что посты автора появляются у тех,
            кто на него подписан"""
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(self.post_follower, response.context['page_obj'])
        self.assertNotIn(
            self.post,
            response.context['page_obj']
        )

    def test_follow_possibility(self):
        response = self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.follower.username}
        ), follow=True)
        self.assertEqual(response.context['following'], True)

    def test_unfollow(self):
        response = self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.follower.username}
        ), follow=True)
        self.assertEqual(response.context['following'], False)

    def test_post_detail_filter(self):
        """Проверка вывода правлиьного поста в подробной информации"""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post_follower.id}
            )
        )
        context_post = response.context.get('post')
        self.assertEqual(context_post.id, self.post_follower.id)
        self.assertEqual(context_post.author, self.post_follower.author)
        self.assertEqual(context_post.text, self.post_follower.text)

    def test_post_edit_correct_context(self):
        """Проверка полей формы при редактировании поста"""
        post = Post.objects.create(
            text='twrtert',
            author=self.user,
        )
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': post.id}
            )
        )
        self.assertEqual(
            response.context.get('form').instance,
            post
        )
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_correct_group_post_creation(self):
        """Проверка правильности группы при выборе таковой"""
        reverses_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse(
                'posts:profile',
                kwargs={'username': self.follower.username}
            )
        ]
        for reverse_name in reverses_list:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context['page_obj'][0]
                self.assertEqual(
                    first_object.group.title,
                    self.post.group.title
                )
                self.assertEqual(
                    first_object.author,
                    self.post_follower.author
                )
                self.assertEqual(
                    first_object.id,
                    self.post_follower.id
                )

    def test_context(self):
        """Проверка правильного контекста на страницах автора и групп"""
        contexts = [
            (reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}),
             'group',
             self.group),
            (reverse(
                'posts:profile',
                kwargs={'username': self.user.username}),
             'user',
             self.user)
        ]
        for tuple in contexts:
            reverse_name, field, expected = tuple
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.context[field], expected)

    def test_cache(self):
        response = self.authorized_client.get(reverse('posts:index')).content
        self.post.delete()
        self.assertEqual(
            response,
            self.authorized_client.get(reverse('posts:index')).content
        )
        cache.clear()
        self.assertNotEqual(
            response,
            self.authorized_client.get(reverse('posts:index')).content
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasBasov')
        cls.group = Group.objects.create(
            title='Leo',
            slug='leo',
        )
        cls.BATCH_SIZE = 26
        objects = [Post(
            group=cls.group,
            author=cls.user,
            text=f'Test {num}') for num in range(cls.BATCH_SIZE)
        ]
        Post.objects.bulk_create(
            islice(objects, cls.BATCH_SIZE),
            cls.BATCH_SIZE
        )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_context_paginator(self):
        """Проверка паджинатора на всех страницах, где он используется"""
        last_page = math.ceil(self.BATCH_SIZE / settings.POSTS_AMOUNT)
        posts_amount_on_last_page = (
            settings.POSTS_AMOUNT - (
                (settings.POSTS_AMOUNT * last_page) - self.BATCH_SIZE
            )
        )
        objects_on_pages = {
            (reverse('posts:index'), settings.POSTS_AMOUNT),
            (reverse(
                'posts:group_list',
                kwargs={'slug': 'leo'}
            ), settings.POSTS_AMOUNT),
            (reverse(
                'posts:profile',
                kwargs={'username': 'StasBasov'}
            ), settings.POSTS_AMOUNT),
            (reverse('posts:index')
                + f'?page={last_page}', posts_amount_on_last_page),
            (reverse('posts:group_list', kwargs={'slug': 'leo'})
                + f'?page={last_page}', posts_amount_on_last_page),
            (reverse('posts:profile', kwargs={'username': 'StasBasov'})
                + f'?page={last_page}', posts_amount_on_last_page),
        }
        for tuple in objects_on_pages:
            reverse_name, expected = tuple
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), expected)
