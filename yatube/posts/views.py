from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect

from .forms import CommentForm, PostForm
from .models import Group, Post, User, Follow

POSTS_ON_PAGE = 10


def paginator(request, post_list):
    paginator_obj = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    return paginator_obj.get_page(page_number)


def index(request):
    post_list = Post.objects.select_related('group').all()
    page_obj = paginator(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.groups.all()
    page_obj = paginator(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author_id=author.id)
    following = False
    if Follow.objects.filter(user=request.user, author=author).exists():
        following = True
    page_obj = paginator(request, post_list)
    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    context = {
        'form': form,
        'is_edit': False,
    }
    if not form.is_valid():
        return render(request, 'posts/post_create.html', context)
    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect('posts:profile', request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        messages.error(request, 'Только автор может редактировать запись')
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    if Follow.objects.filter(user=request.user).exists():
        followed_authors = Follow.objects.filter(user=request.user)
        author_list = []
        for author in followed_authors:
            author_list.append(author.author.id)
        post_list = Post.objects.filter(author_id__in=author_list)
        page_obj = paginator(request, post_list)
        context = {
            'page_obj': page_obj,
        }
        return render(request, 'posts/follow.html', context)
    return redirect('posts:index')


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if not Follow.objects.filter(user=request.user, author=author).exists():
        if request.user == author:
            messages.error(request, 'Нельзя подписаться на самого себя')
            return redirect('posts:profile', author)
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', author)

@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect('posts:profile', author)
