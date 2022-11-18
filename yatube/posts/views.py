from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Follow
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
# Число отображаемых постов на странице

SHOW_SOME_POSTS = 10


def paginator(request, info):
    paginator = Paginator(info, SHOW_SOME_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    template = 'posts/index.html'
    # post_list = Post.objects.all()
    post_list = Post.objects.select_related('author').all()
    page_obj = paginator(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginator(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related("group", "author")
    page_obj = paginator(request, post_list)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        following = False
    profile = author
    index = False
    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following,
        'profile': profile,
        'index': index
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': comments
    }
    return render(request, template, context)


@login_required
def post_create(request):
    is_edit = False
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", request.user)
    context = {
        'form': form,
        'is_edit': is_edit,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    is_edit = True
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST, files=request.FILES or None, instance=post)
    if request.user == post.author:
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:post_detail', post.id)
    context = {
        'post': post,
        'form': form,
        'is_edit': is_edit,
    }
    return render(request, template, context)


@login_required
@csrf_exempt
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts:post_detail', {
        'post': post,
        'form': form
    }
    )


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    list_of_posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(request, list_of_posts)
    index = True
    profile = True
    context = {
        'page_obj': page_obj,
        'index': index,
        'profile': profile
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect(reverse('posts:profile', args=[username]))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    is_follower.delete()
    return redirect('posts:profile', username=author)
