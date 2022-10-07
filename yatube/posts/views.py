from django.contrib.auth.decorators import login_required
from .utils import get_page
from django.shortcuts import render, get_object_or_404, redirect
from .models import Group, Post, User, Follow
from .forms import CommentForm, PostForm
from django.views.decorators.cache import cache_page


@cache_page(60 * 20)
def index(request):
    page_obj = get_page(Post.objects.all(), request)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    title = f'Записи сообщества {group.title}'
    page_obj = get_page(group.posts.all(), request)
    context = {
        'group': group,
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_count = author.posts.all().count()
    title = f'Профайл пользователя {username}'
    page_obj = get_page(author.posts.all(), request)
    following = (request.user.is_authenticated
                 and Follow.objects.filter(
                     user=request.user,
                     author=author).exists())
    context = {
        'title': title,
        'posts_count': posts_count,
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    author_post = post.author
    title = f'Пост {post.text[:30]}'
    form = CommentForm(request.POST)
    comments = post.comments.all()
    context = {
        'post': post,
        'title': title,
        'author_post': author_post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author)
    context = {
        'form': form
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post = Post.objects.filter(author__following__user=request.user)
    page_obj = get_page(post, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author == request.user:
        return redirect(
            'posts:profile',
            username=username
        )
    follower = Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()
    if follower is True:
        return redirect(
            'posts:profile',
            username=username
        )
    Follow.objects.create(user=request.user, author=author)
    return redirect(
        'posts:profile',
        username=username
    )


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user, author=User.objects.get(username=username)
    ).delete()
    return redirect('posts:profile', request.user)
