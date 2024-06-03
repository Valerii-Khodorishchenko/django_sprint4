from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect

from blog.models import Category, Post
from users.models import MyUser
from users.form import CustomUserCreationForm
# from users.views import UserCreateView



def index(request):
    posts = Post.objects.get_published_posts().order_by('id')
    page_obj = Paginator(posts, 10).get_page(request.GET.get('page'))
    return render(request, 'blog/index.html', {'page_obj': page_obj})



def category_posts(request, category_slug):
    category = get_object_or_404(Category.objects.all(), slug=category_slug,
                                 is_published=True)
    return render(request, 'blog/category.html', {
        'category': category,
        'posts': category.posts.get_published_posts(),
    })


def post_detail(request, post_id):
    return render(request, 'blog/detail.html', {
        'post': get_object_or_404(Post.objects.get_published_posts(),
                                  pk=post_id)
    })


def profile(request, username):
    template_name = 'blog/profile.html'
    user = MyUser.objects.get(username=username)
    context = {'profile': user}
    return render(request, template_name, context)

def create_post(request):
    pass

# @login_required
# def edit_profile(request):
#     template_name = 'blog/user.html'
#     return render(request, template_name, {'form': form})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('blog:profile', username=request.user)  # Перенаправление на страницу профиля или другую страницу
    else:
        form = CustomUserCreationForm(instance=request.user)

    return render(request, 'blog/user.html', {'form': form})
