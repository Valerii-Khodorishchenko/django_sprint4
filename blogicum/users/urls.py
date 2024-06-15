from django.urls import include, path

from blog.views import ProfileDetailView
from . import views


urlpatterns = [
    path('registration/', views.UserCreateView.as_view(), name='registration'),
    path('edit/', views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('<slug:username>/', ProfileDetailView.as_view(),
         name='profile'),
    path('', include('django.contrib.auth.urls'), name='login'),
]
