from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Nameless')
        cls.group = Group.objects.create(
            title='Test-group',
            slug='t-group',
            description='test-description'
        )
        cls.post = Post.objects.create(
            text='Тестовый заголовок',
            author=cls.author,
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        tested_post = Post.objects.order_by('id').last()

        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
            group=tested_post.group,
            author=tested_post.author,
            text=tested_post.text).exists()
        )

    def test_edit_post(self):
        old_post = self.post
        form_data = {
            'text': 'Новый тестовый текст',
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        new_post = Post.objects.get(id=self.post.id)
        self.assertNotEqual(old_post.text, new_post.text)
