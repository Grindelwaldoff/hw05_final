import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings

from posts.models import Comment, Post, Group


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='Stas')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
        )

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)
        SMALL_GIF = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        self.post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
            group=self.group,
            image=''
        )

    def _test_context_on_page(self, list):
        for tuple in list:
            expected, real = tuple
            with self.subTest(expected=expected):
                return self.assertEqual(expected, real)

    def test_form_exists(self):
        """Проверка формы по создании постов"""
        Post.objects.all().delete()
        form_data = {
            'text': 'Тестовый пост 123',
            'group': self.group.pk,
            'author': self.user.id,
            'image': self.uploaded.open(),
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        first_object = Post.objects.all().first()
        first_object_list = [
            (first_object.text, form_data['text']),
            (first_object.group.pk, form_data['group']),
            (first_object.author.id, form_data['author']),
            (first_object.image, form_data['image']),
        ]
        self._test_context_on_page(first_object_list)
        self.assertEqual(Post.objects.count(), 1)
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )

    def test_form_Comment(self):
        Comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый коммент'
        }
        response = self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(
            response.context['comment'].count(),
            Comment_count + 1
        )

    def test_form_post_edit(self):
        """Проверка формы изменения поста и применени этих изменений в БД"""
        form_data = {
            'text': 'Не тестовый пост',
            'group': self.group.pk,
            'image': self.uploaded.open(),
        }
        response = self.client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        first_object = Post.objects.get(id=self.post.id)
        first_object_list = [
            (first_object.text, form_data['text']),
            (first_object.group.pk, form_data['group']),
            (first_object.author.id, self.post.author.id),
            (first_object.image, form_data['image']),
        ]
        self._test_context_on_page(first_object_list)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
