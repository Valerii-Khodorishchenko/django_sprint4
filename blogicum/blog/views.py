from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView)

from .form import CommentsForm, PostForm
from .models import Category, Comments, Post

User = get_user_model()


class ConfirmAuthorMixin:
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.is_published and obj.author != request.user:
            raise Http404("Пост не опкбликован")
        return super().dispatch(request, *args, **kwargs)


class FormValidMixin:
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.get_object().pk)


class PostChangeMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'


class CommentsCountMixin:
    model = Post
    paginate_by = 10
    queryset = Comments.objects.prefetch_related('author')

    def get_queryset(self):
        return Post.posts_objects.get_published_posts()


class PostCreateView(FormValidMixin, LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(FormValidMixin, OnlyAuthorMixin, PostChangeMixin,
                     UpdateView):
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.pk})


class PostDeleteView(OnlyAuthorMixin, PostChangeMixin, DeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )

    def handle_no_permission(self):
        return redirect('blog:profile', username=self.request.user)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = super().get_object(queryset=queryset)
        if post.pub_date > timezone.now() and post.author != self.request.user:
            raise Http404("Post not found")
        if not post.is_published and post.author != self.request.user:
            raise Http404("Post not found")
        if not post.category.is_published and post.author != self.request.user:
            raise Http404("Category not found")
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentsForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class PostsListView(CommentsCountMixin, ListView):
    template_name = 'blog/index.html'


class CategoryPostListView(CommentsCountMixin, ListView):
    template_name = 'blog/category.html'

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        return super().get_queryset().filter(category__slug=category_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not hasattr(self, '_cached_category'):
            category_slug = self.kwargs['category_slug']
            self._cached_category = get_object_or_404(
                Category.objects.all(), slug=category_slug, is_published=True
            )
        context['category'] = self._cached_category
        return context

# TODO: Измавь запрос
class ProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'
    context_object_name = 'profile'

    def get_object(self):
        username = self.kwargs['username']
        return get_object_or_404(User, username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        if self.request.user.username == user.username:
            posts = (user
                     .posts(manager='posts_objects')
                     .get_user_post_cards(user)
                     )
        else:
            posts = (user
                     .posts(manager='posts_objects')
                     .get_other_user_post_cards(user)
                     )
        paginator = Paginator(posts, 10)
        page = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page)
        return context


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentsForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comments, pk=comment_id, post=post)

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        form = CommentsForm(request.POST, instance=comment)

        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentsForm(instance=comment)
    return render(request, 'blog/comment.html', {
        'form': form,
        'post': post,
        'comment': comment
    })


@login_required
def delete_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comments, pk=comment_id, post=post)

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html', {'post': post,
                                                 'comment': comment})
