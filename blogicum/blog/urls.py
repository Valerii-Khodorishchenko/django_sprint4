from django.urls import include, path

from . import views

app_name = 'blog'


urlpatterns = [
    # TODO: После тестов попробуй перенести профиль в юзер

    # path('profile/<slug:username>/', profile, name='profile'),
    path('profile/', include('users.urls')),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    # path('posts/create/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/edit/', views.PostUpdateView.as_view(),
         name='edit_post'),
    # path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:post_id>/delete/',
         views.PostDeleteView.as_view(), name='delete_post'),
    # path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('posts/<int:post_id>/comment/', views.add_comment,
         name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<comment_id>', views.edit_comment,
         name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<comment_id>',
         views.delete_comment, name='delete_comment'),
    path('posts/<int:post_id>/', views.PostDetailView.as_view(),
         name='post_detail'),
    # path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/',
         views.CategoryPostListView.as_view(), name='category_posts'),
    # path('category/<slug:category_slug>/', views.category_posts,
    #      name='category_posts'),
    path('', views.PostsListView.as_view(), name='index'),
    # path('', views.index, name='index'),
]
