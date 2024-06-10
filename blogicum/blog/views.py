from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView, ListView, UpdateView, DeleteView, DetailView)
# from django.views.generic.edit import CreateView
# from django.utils import timezone


from .form import CommentsForm, PostForm
from .models import Category, Comments, Post
# from users.models import MyUser
# from users.form import CustomUserCreationForm
# from users.views import UserCreateView
# TODO: Удали коментарии


# TODO Представления на основе классов
class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.get_object().pk)
    

class CommentsCountMixin:
    model = Post
    paginate_by = 10
    queryset = Comments.objects.prefetch_related('author')

    def get_queryset(self):
        return Post.objects.get_published_posts().annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date', 'title')



class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    # TODO: миксин с Изменением
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.pk})


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentsForm()
        context['comments'] = self.object.comments.select_related('author')
        return context

    def get_success_url(self):
        return redirect('blog:post_detail', kwargs={'post_id': self.object.pk})


class PostsListView(CommentsCountMixin, ListView):
    template_name = 'blog/index.html'

    # def get_queryset(self):
    #     return Post.objects.get_published_posts().annotate(
    #         comment_count=Count('comments')
    #     ).order_by('-pub_date', 'title')


class CategoryPostListView(CommentsCountMixin, ListView):
    template_name = 'blog/category.html'

    # def get_queryset(self):
    #     category_slug = self.kwargs.get('category_slug')
    #     return Post.objects.get_published_posts(
    #     ).annotate(
    #         comment_count=Count('comments')
    #     ).order_by('-pub_date', 'title').filter(category__slug=category_slug)

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


# TODO Представления на основе функций

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user)
    form = PostForm()
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post.pk)
        return render(request, 'blog/create.html', {'form': form})
    form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST, instance=post)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user)
    return render(request, 'blog/create.html', {'form': form})


def post_detail(request, post_id):
    return render(request, 'blog/detail.html', {
        'post': get_object_or_404(Post.objects.get_published_posts(),
                                  pk=post_id)
    })


def index(request):
    posts = Post.objects.get_published_posts().order_by('-pub_date', 'title')
    page_obj = Paginator(posts, 10).get_page(request.GET.get('page'))
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def category_posts(request, category_slug):
    posts = Post.objects.get_published_posts(
    ).filter(
        category__slug=category_slug
    ).order_by('-pub_date', 'title')
    print(category_slug)
    page_obj = Paginator(posts, 10).get_page(request.GET.get('page'))
    category = get_object_or_404(Category.objects.all(), slug=category_slug,
                                 is_published=True)
    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj,
    })


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


# def delete_comment(request, pk):
#     return HttpResponse('Удалить коментарий')
