from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post


User = get_user_model()


class PostModelsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Leo',
            slug='leo',
            description='ya ne leo'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_correct_objects_names(self):
        values = [
            (str(self.post), self.post.text[:Post.FIRST_FIFTEEN_SIMBOLS]),
            (str(self.group), self.group.title)
        ]
        for tuple in values:
            check, expected = tuple
            with self.subTest(expected=expected):
                self.assertEqual(check, expected)

    def test_post_have_help_text(self):
        """Проверка на наличие help_text у модели Post"""
        field_help_texts = [
            ('text', 'Введите текст:'),
            ('author', 'Выберите пользователя'),
            ('group', 'Выберите группу'),
        ]
        for tuple in field_help_texts:
            field, value = tuple
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text,
                    value
                )

    def test_post_have_verbose_name(self):
        field_verbose_name = [
            ('text', 'Что у вас нового?'),
            ('created', 'Дата создания'),
            ('author', 'Имя пользователя'),
            ('group', 'Название группы'),
        ]
        for tuple in field_verbose_name:
            field, value = tuple
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    value
                )
