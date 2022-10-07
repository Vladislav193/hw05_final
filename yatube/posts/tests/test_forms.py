import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, Comment
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug4'
        )
        cls.author = User.objects.create(username='1')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст2',
            author=cls.author,
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_post_with_image(self):
        """При отправке поста с картинкой через форму 
        создаётся запись в базе данных.
        """
        form_data = {
            'text': 'Тестовый текст2',
            'group': self.group.id,
            'author': self.author,
            'image': self.uploaded,
        }
        posts_count = Post.objects.count()
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        self.assertEqual(
            Post.objects.count(), posts_count
        )
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                text='Тестовый текст2',
                image='posts/small.gif'
            ).exists()
        )

    def test_create_post_form(self):
        """При отправке валидной формы происходит изменение поста в БД
         и после успешной отправки комментарий появляется на странице поста."""
        posts_count = Post.objects.count()
        comments_count = Comment.objects.count()
        form_date = {
            'text': 'Измененый текст'
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_date,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertTrue(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}), )
