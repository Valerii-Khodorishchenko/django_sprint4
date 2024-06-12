from django.urls import include, path

from . import views


urlpatterns = [
    path('registration/', views.UserCreateView.as_view(), name='registration'),
    path('edit/', views.ProfileUpdateView.as_view(), name='edit_profile'),
<<<<<<< HEAD
    path('<slug:username>/', views.ProfileDetailView.as_view(),
         name='profile'),
=======
    # path('<slug:username>/edit/>', views.edit_profile, name='edit_profile'),
    # path('edit/', views.edit_profile, name='edit_profile'),
    path('<slug:username>/', views.ProfileDetailView.as_view(), name='profile'),
    # path('<slug:username>/', views.profile, name='profile'),
>>>>>>> 6ba8cd4bdf27b74e5f926cb44eaca490ac29a0a6
    path('', include('django.contrib.auth.urls'), name='login'),
]
