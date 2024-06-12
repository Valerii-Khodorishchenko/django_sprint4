from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from blog.models import Post
from .models import MyUser
from .form import CustomUserCreationForm, CustomUserChangeForm


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
