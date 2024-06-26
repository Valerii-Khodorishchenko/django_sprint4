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

PAGINATOR_BY = 10

User = get_user_model()


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
    paginate_by = PAGINATOR_BY
    queryset = Comments.objects.prefetch_related('author')


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
        return get_object_or_404(Post,
                                 id=post.id,
                                 is_published=True,
                                 category__is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentsForm()
        context['comments'] = (self.object.post_comments
                               .select_related('author'))
        return super().get_context_data(
            **kwargs,
            form=CommentsForm(),
            comments=self.object.post_comments.select_related('author')
        )


class PostsListView(CommentsCountMixin, ListView):
    template_name = 'blog/index.html'

    def get_queryset(self):
        return Post.posts.get_published_posts()


class CategoryPostListView(CommentsCountMixin, ListView):
    template_name = 'blog/category.html'

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(Category, slug=category_slug)
        return category.categorized_posts.filter_published()

    def get_context_data(self, **kwargs):
        slug = self.kwargs['category_slug']
        return super().get_context_data(
            **kwargs,
            category=Category.objects.get_published_category(slug)
        )


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
        user = self.get_object()
        if self.request.user.username == user.username:
            posts = (user
                     .authored_posts(manager='posts')
                     .get_user_post_cards(user)
                     )
        else:
            posts = (user
                     .authored_posts(manager='posts')
                     .get_other_user_post_cards(user)
                     )
        paginator = Paginator(posts, PAGINATOR_BY)
        page = self.request.GET.get('page')
        return super().get_context_data(
            **kwargs,
            page_obj=paginator.get_page(page)
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
