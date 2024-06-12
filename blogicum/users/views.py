from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from django.shortcuts import get_object_or_404
from django.http import Http404

from blog.models import Post, Comments
from blog.views import CommentsCountMixin
from .models import MyUser
from .form import CustomUserCreationForm, CustomUserChangeForm

from django.contrib.auth import get_user_model


User = get_user_model()


class UserCreateView(CreateView):
    model = MyUser
    form_class = CustomUserCreationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        return response


class ProfileDetailView(DetailView):
    model = MyUser
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'
    context_object_name = 'profile'

    def get_object(self):
        username = self.kwargs.get('username')
        return get_object_or_404(User, username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        if self.request.user.username == user.username:
            # Отображаем все посты пользователя
            posts = Post.objects.select_related(
                'location', 'author', 'category'
            ).filter(
                author=user
            ).order_by(
                '-pub_date',
                'title'
            ).annotate(
                comment_count=Count('comments')
            )
        else:
            # Отображаем только опубликованные посты
            posts = Post.objects.get_published_posts(
            ).filter(
                author=user
            ).order_by(
                '-pub_date',
                'title'
            ).annotate(
                comment_count=Count('comments')
            )
        paginator = Paginator(posts, 10)
        page = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page)
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = MyUser
    form_class = CustomUserChangeForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('blog:profile', username=user.username)


# TODO: Удалить FBV
def profile(request, username):
    template_name = 'blog/profile.html'
    user = MyUser.objects.get(username=username)
    posts = Post.objects.get_published_posts(
    ).filter(
        author=user
    ).order_by(
        '-pub_date',
        'title'
    )
    page_obj = Paginator(posts, 10).get_page(request.GET.get('page'))
    context = {
        'profile': user,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


# @login_required
# def edit_profile(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST, instance=request.user)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             messages.success(request, 'Your profile was successfully updated!')
#             return redirect('blog:profile', username=request.user)
#     else:
#         form = CustomUserCreationForm(instance=request.user)

#     return render(request, 'blog/user.html', {'form': form})

@login_required
def edit_profile(request, username):
    instance = get_object_or_404(User, username=username)
    if instance != request.user:
        print('error')
        raise Http404
    form = CustomUserUpdateForm(request.POST or None, instance=instance)
    context = {'form': form}
    print('error1')
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('blog:profile', username=request.user)
    print('error2')
    return render(request, 'blog/user.html', {'form': form})
