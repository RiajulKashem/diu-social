from django.db.models import Q

from notification.models import Notification
from django.core.checks import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView,
    DeleteView,
)
from .models import Comment, Post
from .forms import CommentForm
from django.http import HttpResponseRedirect, JsonResponse
from users.models import Profile
from itertools import chain
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
import random
from blog.utils import is_ajax

""" Home page with all posts """


def home(request):
    context = {
        'posts': Post.objects.all().prefetch_related('comments')
    }
    return render(request, 'blog/home_page.html', context)


""" Posts of following user profiles """


@login_required
def posts_of_following_profiles(request):

    profile = Profile.objects.get(user=request.user)
    users = [user for user in profile.following.all()]
    posts = []
    qs = None
    for u in users:
        p = Profile.objects.get(user=u)
        p_posts = p.user.post_set.all()
        posts.append(p_posts)
    my_posts = profile.profile_posts()
    posts.append(my_posts)
    if len(posts) > 0:
        qs = sorted(
            chain(*posts), reverse=True, key=lambda obj: obj.date_posted
        )

    paginator = Paginator(qs, 5)
    page = request.GET.get('page')
    try:
        posts_list = paginator.page(page)
    except PageNotAnInteger:
        posts_list = paginator.page(1)
    except EmptyPage:
        posts_list = paginator.page(paginator.num_pages)

    return render(
        request, 'blog/feeds.html', {'profile': profile, 'posts': posts_list}
    )


""" Post Like """


@login_required
def like_post(request):
    post = get_object_or_404(Post, id=request.POST.get('id'))
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        notify = Notification.objects.filter(
            post=post, sender=request.user, notification_type=1
        )
        notify.delete()
    else:
        post.likes.add(request.user)
        notify = Notification(
            post=post, sender=request.user, user=post.author,
            notification_type=1
        )
        notify.save()

    html = render_to_string(
        'blog/like_section.html', {'post': post}, request=request
    )
    return JsonResponse({'html': html})


""" Post save """


@login_required
def SaveView(request):

    post = get_object_or_404(Post, id=request.POST.get('id'))
    saved = False
    if post.saves.filter(id=request.user.id).exists():
        post.saves.remove(request.user)
        saved = False
    else:
        post.saves.add(request.user)
        saved = True

    context = {
        'post': post,
        'total_saves': post.total_saves(),
        'saved': saved,
    }

    if is_ajax(request=request):
        html = render_to_string(
            'blog/save_section.html', context, request=request
        )
        return JsonResponse({'form': html})


@login_required
def like_comment_view(request):
    comment = get_object_or_404(Comment, id=request.POST.get('comment_id'))
    if comment.likes.filter(id=request.user.id).exists():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    post.refresh_from_db()
    html = render_to_string(
        'blog/comments.html', {'post': post}, request=request
    )
    return JsonResponse({'html': html})


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_context_data(self, *args, **kwargs):
        context = super(PostListView, self).get_context_data()
        users = list(User.objects.exclude(pk=self.request.user.pk))
        if len(users) > 3:
            cnt = 3
        else:
            cnt = len(users)
        random_users = random.sample(users, cnt)
        context['random_users'] = random_users
        return context


""" All the posts of the user """


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


""" Post detail view """


def PostDetailView(request, pk):
    return render(
        request, 'blog/post_detail.html',
        {'post': get_object_or_404(Post, pk=pk)}
    )


""" Create post """


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'featured_image', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


""" Update post """


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'featured_image', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


""" Delete post """


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


""" About page """


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})


""" Search by post title or username """


def search(request):
    query = request.GET['query']
    if len(query) >= 150 or len(query) < 1:
        allposts = Post.objects.none()
    elif len(query.strip()) == 0:
        allposts = Post.objects.none()
    else:
        allposts = Post.objects.filter(
            Q(title__icontains=query) | Q(author__username__icontains=query)
        )
    params = {'allposts': allposts}
    return render(request, 'blog/search_results.html', params)


""" Liked posts """


@login_required
def AllLikeView(request):
    user = request.user
    liked_posts = user.blogpost.all()
    context = {
        'liked_posts': liked_posts
    }
    return render(request, 'blog/liked_posts.html', context)


""" Saved posts """


@login_required
def AllSaveView(request):
    user = request.user
    saved_posts = user.blogsave.all()
    context = {
        'saved_posts': saved_posts
    }
    return render(request, 'blog/saved_posts.html', context)


@login_required()
def comment_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    print(request.POST)
    if request.method == 'POST':
        text = request.POST.get('text')
        comment = Comment.objects.create(
            post=post, name=request.user, body=text
        )
        reply_id = request.POST.get('reply_id', None)
        if reply_id:
            comment.reply_id = int(reply_id)
            comment.save()
    post.refresh_from_db()
    html = render_to_string(
        'blog/comments.html', {'post': post}, request=request
    )
    return JsonResponse({'html': html})
