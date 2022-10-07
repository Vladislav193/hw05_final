from xml.etree.ElementTree import Comment
from django.forms import ModelForm
from .models import Post, Comment
from django import forms


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text', 'image']
        labels = {'group': 'Группа', 'text': 'Сообщение'}
        help_texts = {'group': 'Выберите группу', 'text': 'Введите ссообщение'}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Комментарий'}
        helps_texts = {'text': 'Текст комментрия'}
