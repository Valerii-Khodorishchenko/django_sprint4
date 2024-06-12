from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView)

from .form import CommentsForm, PostForm
from .models import Category, Comments, Post
<<<<<<< HEAD
=======
# from users.models import MyUser
# from users.form import CustomUserCreationForm
# from users.views import UserCreateView
# TODO: Удали коментарии
from django.shortcuts import get_object_or_404
from django.http import Http404

class ConfirmAuthorMixin:
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.is_published and obj.author != request.user:
            raise Http404("Пост не опкбликован")
        return super().dispatch(request, *args, **kwargs)
>>>>>>> 6ba8cd4bdf27b74e5f926cb44eaca490ac29a0a6


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


<<<<<<< HEAD
class PostChangeMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
=======
>>>>>>> 6ba8cd4bdf27b74e5f926cb44eaca490ac29a0a6


class CommentsCountMixin:
    model = Post
    paginate_by = 10
    queryset = Comments.objects.prefetch_related('author')

    def get_queryset(self):
        return Post.objects.get_published_posts().annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date', 'title')


<<<<<<< HEAD
class PostCreateView(FormValidMixin, LoginRequiredMixin, CreateView):
=======
class PostCreateView(LoginRequiredMixin, CreateView):
>>>>>>> 6ba8cd4bdf27b74e5f926cb44eaca490ac29a0a6
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


from django.http import Http404
from django.utils import timezone
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
# class PostDetailView(DetailView):
#     model = Post
#     template_name = 'blog/detail.html'
#     pk_url_kwarg = 'post_id'

<<<<<<< HEAD
=======
#     def get_object(self, queryset=None):
#         post = super().get_object(queryset=queryset)
#         if not post.is_published and post.author != self.request.user:
#             raise Http404("Post not found")
#         if not post.category.is_published and post.author != self.request.user:
#             raise Http404("Category not found")
#         return post

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['form'] = CommentsForm()
#         context['comments'] = self.object.comments.select_related('author')
#         return context

#     def get_success_url(self):
#         return redirect('blog:post_detail', kwargs={'post_id': self.object.pk})

>>>>>>> 6ba8cd4bdf27b74e5f926cb44eaca490ac29a0a6

class PostsListView(CommentsCountMixin, ListView):
    template_name = 'blog/index.html'


class CategoryPostListView(CommentsCountMixin, ListView):
    template_name = 'blog/category.html'

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        return super().get_queryset().filter(category__slug=category_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not hasattr(self, '_cached_category'):
            category_slug = self.kwargs.get('category_slug')
            self._cached_category = get_object_or_404(
                Category.objects.all(), slug=category_slug, is_published=True
            )
        context['category'] = self._cached_category
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

    return render(request, 'blog/comment.html', {'post': post, 'comment': comment})
