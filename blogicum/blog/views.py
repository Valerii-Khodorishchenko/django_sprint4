from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView)

from .form import CommentsForm, CustomUserChangeForm, PostForm
from .models import Category, Comments, Post, User, get_filtered_posts


PAGINATOR_BY = 10


class FormValidMixin:
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.get_object().pk)


class PostChangeMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'


class CommentsCountMixin:
    model = Post
    paginate_by = PAGINATOR_BY
    queryset = Comments.objects.select_related('author')


class PostCreateView(FormValidMixin, LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class PostUpdateView(FormValidMixin, OnlyAuthorMixin, PostChangeMixin,
                     UpdateView):
    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.object.pk])


class PostDeleteView(OnlyAuthorMixin, PostChangeMixin, DeleteView):
    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            form=PostForm(instance=self.object)
        )

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = super().get_object(queryset=queryset,)
        if post.author == self.request.user:
            return post
        return get_object_or_404(
            get_filtered_posts(Post.objects, comment_count=False),
            id=post.id
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            form=CommentsForm(),
            comments=self.object.comments.select_related('author')
        )


class PostsListView(CommentsCountMixin, ListView):
    template_name = 'blog/index.html'
    queryset = get_filtered_posts(Post.objects)


class CategoryPostListView(CommentsCountMixin, ListView):
    template_name = 'blog/category.html'

    def get_queryset(self):
        category = self.get_category()
        return get_filtered_posts(category.posts)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, category=self.get_category())

    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )


class ProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        author = self.get_object()
        posts = get_filtered_posts(
            author.posts,
            filter_published=(self.request.user.username != author.username),
        )
        paginator = Paginator(posts, PAGINATOR_BY)
        page = self.request.GET.get('page')
        return super().get_context_data(
            **kwargs,
            page_obj=paginator.get_page(page)
        )


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


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
    comment = get_object_or_404(
        Comments.objects.select_related('post'),
        pk=comment_id,
        post_id=post_id
    )
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    form = CommentsForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=comment.post.id)
    return render(request, 'blog/comment.html', {
        'form': form,
        'post': comment.post,
        'comment': comment,
    })


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comments.objects.select_related('post'),
        pk=comment_id,
        post_id=post_id
    )
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {'post': comment.post,
                                                 'comment': comment})
