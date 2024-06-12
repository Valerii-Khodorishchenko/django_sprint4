from django.urls import path
from django.urls import include

from . import views


urlpatterns = [
    path('registration/', views.UserCreateView.as_view(), name='registration'),
    path('edit/', views.ProfileUpdateView.as_view(), name='edit_profile'),
    # path('<slug:username>/edit/>', views.edit_profile, name='edit_profile'),
    # path('edit/', views.edit_profile, name='edit_profile'),
    path('<slug:username>/', views.ProfileDetailView.as_view(), name='profile'),
    # path('<slug:username>/', views.profile, name='profile'),
    path('', include('django.contrib.auth.urls'), name='login'),
]
