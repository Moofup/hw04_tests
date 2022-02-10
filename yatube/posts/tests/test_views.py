from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from .. import views
from ..models import Group, Post


User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Nameless')
        cls.group = Group.objects.create(
            title='Test-group',
            slug='t-group',
            description='test-description'
        )
        for i in range(1, 14):
            cls.post = Post.objects.create(
                text='Тестовый текст ' + str(i),
                author=cls.author,
                group=cls.group
            )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.author.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def objects_test(self, tested_object):
        self.assertEqual(tested_object, self.post)

    def test_index_shows_correct_context(self):
        group3 = Group.objects.create(
            title='3dTest-group',
            slug='3dt-group',
            description='3dtest-description'
        )
        post = Post.objects.create(
            text='Третьезаданьевский текст',
            author=self.author,
            group=group3
        )
        response = self.authorized_client.get(reverse('posts:index'))
        test_object = response.context.get('page_obj')[1]
        test_title = response.context['title']
        test_second_page_count = (
            self.author.posts.count() - views.MAX_POST_DISPLAYED
        )
        self.objects_test(test_object)
        self.assertEqual(test_title, 'Последние обновления на сайте')
        self.assertIn(post, response.context.get('page_obj'))
        self.assertEqual(
            len(response.context['page_obj']),
            views.MAX_POST_DISPLAYED
        )
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            test_second_page_count
        )

    def test_group_list_shows_correct_context(self):
        group3 = Group.objects.create(
            title='3dTest-group',
            slug='3dt-group',
            description='3dtest-description'
        )
        post = Post.objects.create(
            text='Третьезаданьевский текст',
            author=self.author,
            group=group3
        )
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}))
        test_object = response.context.get('page_obj')[0]
        test_title = response.context['title']
        test_group = response.context['group']
        test_second_page_count = (
            self.author.posts.count() - views.MAX_POST_DISPLAYED - 1
        )
        self.objects_test(test_object)
        self.assertEqual(test_title, 'Записи сообщества Test-group')
        self.assertEqual(test_group, self.group)
        self.assertNotIn(post, response.context.get('page_obj'))
        self.assertEqual(
            len(response.context['page_obj']),
            views.MAX_POST_DISPLAYED
        )
        response = (
            self.client.get(reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}) + '?page=2')
        )
        self.assertEqual(
            len(response.context['page_obj']),
            test_second_page_count
        )
        response = (
            self.authorized_client.get(reverse(
                'posts:group_list',
                kwargs={'slug': group3.slug}))
        )
        self.assertIn(post, response.context.get('page_obj'))

    def test_profile_shows_correct_context(self):
        group3 = Group.objects.create(
            title='3dTest-group',
            slug='3dt-group',
            description='3dtest-description'
        )
        post = Post.objects.create(
            text='Третьезаданьевский текст',
            author=self.author,
            group=group3
        )
        response = (
            self.authorized_client.get(reverse(
                'posts:profile',
                kwargs={'username': self.author.username}))
        )
        test_object = response.context.get('page_obj')[1]
        test_title = response.context['title']
        test_author = response.context['author']
        test_post_count = response.context['author_posts_count']
        test_second_page_count = (
            self.author.posts.count() - views.MAX_POST_DISPLAYED
        )
        self.objects_test(test_object)
        self.assertEqual(test_title, 'Все посты пользователя Nameless')
        self.assertEqual(test_author, self.author)
        self.assertEqual(test_post_count, self.author.posts.count())
        self.assertIn(post, response.context.get('page_obj'))
        self.assertEqual(
            len(response.context['page_obj']),
            views.MAX_POST_DISPLAYED
        )
        response = (
            self.client.get(reverse(
                'posts:profile',
                kwargs={'username': self.author.username}) + '?page=2')
        )
        self.assertEqual(
            len(response.context['page_obj']),
            test_second_page_count
        )

    def test_post_detail_shows_correct_context(self):
        response = (
            self.authorized_client.get(reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}))
        )
        test_title = response.context['title']
        test_post = response.context['post']
        test_post_count = response.context['author_posts_count']
        self.assertEqual(test_title, self.post.text)
        self.assertEqual(test_post, self.post)
        self.assertEqual(test_post_count, self.post.author.posts.count())

    def test_edit_post_shows_correct_context(self):
        response = (
            self.authorized_client.get(reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}))
        )
        test_is_edit = response.context['is_edit']
        form_fields = {
            'text': forms.fields.CharField,
        }
        form_field = response.context.get('form').fields.get('text')
        self.assertIsInstance(form_field, form_fields['text'])
        self.assertTrue(test_is_edit)

    def test_post_create_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.MultipleChoiceField,
        }
        form_field = response.context.get('form').fields.get('text')
        self.assertIsInstance(form_field, form_fields['text'])
