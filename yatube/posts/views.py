from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page

from posts.models import Follow, Comment, Post, Group, User
from posts.forms import PostForm, GroupForm, CommentForm


def paginator_function(
        objects,
        page_number,
        page_amount=settings.POSTS_AMOUNT):
    paginator = Paginator(objects, page_amount)
    return paginator.get_page(page_number)


@cache_page(20, key_prefix='/')
def index(request):
    posts = Post.objects.select_related('author', 'group')
    page_number = request.GET.get('page')
    context = {
        'page_obj': paginator_function(posts, page_number),
    }
    return render(request, 'posts/index.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts_author.select_related('group')
    page_number = request.GET.get('page')
    status = False

    if request.user.is_authenticated and Follow.objects.filter(
            user__follower__user=request.user).exists():
        status = True

    context = {
        'author': author,
        'page_obj': paginator_function(posts, page_number),
        'following': status,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        id=post_id
    )
    comments = Comment.objects.filter(post_id__comments__post=post_id)
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts_group.select_related('author')
    page_number = request.GET.get('page')
    context = {
        'group': group,
        'page_obj': paginator_function(posts, page_number),
    }
    return render(request, 'posts/group_list.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return redirect('posts:profile', post.author)

    context = {
        'form': form,
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def group_create(request):
    form = GroupForm(request.POST or None)

    if form.is_valid():
        group = form.save(commit=False)
        group.save()

        return redirect('posts:group_list', group.slug)

    context = {
        'form': form,
    }

    return render(request, 'posts/group_create.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        id=post_id
    )

    if request.user != post.author:
        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()

        return redirect('posts:post_detail', post_id)

    context = {
        'form': form,
        'is_edit': True
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
    posts = Post.objects.filter(author__following__user=request.user)
    page_number = request.GET.get('page')
    context = {
        'page_obj': paginator_function(posts, page_number)
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.get(
        user=request.user,
        author=author
    ).delete()
    return redirect('posts:profile', username=username)
