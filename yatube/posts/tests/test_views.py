from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from posts.utils import PAGINATOR_PAGE
from django.core.cache import cache


from posts.models import Group, Post, Follow

TEST_POST: int = 13
User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Test')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug1'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/post_create.html': reverse('posts:post_create'),
            'posts/post_detail.html': (
                reverse('posts:post_detail',
                        kwargs={'post_id': f'{self.post.pk}'})),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={'username': 'Test'}),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'test-slug1'})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Шаблон post_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_group_0, self.group)

    def test_group_list_page_correct_context(self):
        '''Проверяем, что в список постов передается правильный контекст '''
        response = self.authorized_client.get(reverse('posts:group_list',
                                              kwargs={'slug': 'test-slug1'}))
        self.assertEqual(response.context['group'], self.group)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail', kwargs={'post_id': '1'})))
        self.assertEqual(response.context.get('post').text, 'Тестовый пост')

    def test_post_create_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_context(self):
        response = (self.authorized_client.get(reverse
                    ('posts:post_edit', kwargs={'post_id': self.post.id})))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUp(self):
        super().setUpClass()
        self.user = User.objects.create(username='Test')
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug2',
        )
        posts = []
        for _ in range(TEST_POST):
            post = Post(
                author=self.user,
                text='Тестовый пост',
                group=self.group
            )
            posts.append(post)
        Post.objects.bulk_create(posts)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        cache.clear()
        '''Проверка: количество постов на первой странице равно 10.'''
        urls = {
            reverse('posts:index'): 'index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug2'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'Test'}): 'profile.html',
        }

        for tested_url in urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(len(response.context['page_obj']), PAGINATOR_PAGE)

    def test_second_page_contains_three_records(self):
        cache.clear()
        '''Проверка: на второй странице должно быть три поста.'''
        urls = {
            reverse('posts:index') + '?page=2': 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug2'}) + '?page=2':
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'Test'}) + '?page=2':
            'profile.html',
        }
        posts_count = TEST_POST - PAGINATOR_PAGE

        for tested_url in urls.keys():
            response = self.client.get(tested_url)
            self.assertEqual(len(response.context['page_obj']), posts_count)


class CacheViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='test_user')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug5'
        )
        cls.post = Post.objects.create(
            text='test_post',
            group=cls.group,
            author=cls.author
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

    def test_cache_index(self):
        """проверка кэша"""
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            text='test_new_post',
            author=CacheViewsTest.author,
        )
        response_old = self.authorized_client.get(
            reverse('posts:index')
        )
        old_posts = response_old.content
        self.assertEqual(
            old_posts,
            posts,
            'Не возвращает кэшированную страницу.'
        )
        cache.clear()
        response_new = CacheViewsTest.authorized_client.get(reverse
                                                            ('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts, 'Кэш не сбросился')


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_autor = User.objects.create(
            username='post_autor',
        )
        cls.post_follower = User.objects.create(
            username='post_follower',
        )
        cls.post = Post.objects.create(
            text='Подписка',
            author=cls.post_autor,
        )

    def setUp(self):
        cache.clear()
        self.author_client = Client()
        self.author_client.force_login(self.post_follower)
        self.follower_client = Client()
        self.follower_client.force_login(self.post_autor)

    def test_follow_on_user(self):
        """Проверка подписки на пользователя."""
        count_follow = Follow.objects.count()
        self.follower_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.post_follower}))
        follow = Follow.objects.all().latest('id')
        self.assertEqual(Follow.objects.count(), count_follow + 1)
        self.assertEqual(follow.author_id, self.post_follower.id)
        self.assertEqual(follow.user_id, self.post_autor.id)

    def test_unfollow_on_user(self):
        """Проверка отписки от пользователя."""
        Follow.objects.create(
            user=self.post_autor,
            author=self.post_follower)
        count_follow = Follow.objects.count()
        self.follower_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.post_follower}))
        self.assertEqual(Follow.objects.count(), count_follow - 1)

    def test_follow_on_authors(self):
        """Проверка записей у тех кто подписан."""
        post = Post.objects.create(
            author=self.post_autor,
            text="Подписка")
        Follow.objects.create(
            user=self.post_follower,
            author=self.post_autor)
        response = self.author_client.get(
            reverse('posts:follow_index'))
        self.assertIn(post, response.context['page_obj'].object_list)

    def test_notfollow_on_authors(self):
        """Проверка записей у тех кто не подписан."""
        post = Post.objects.create(
            author=self.post_autor,
            text="Подписка")
        response = self.author_client.get(
            reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page_obj'].object_list)
