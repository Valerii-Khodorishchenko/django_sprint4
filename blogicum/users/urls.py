from django.urls import path
from django.urls import include

from .import views


app_name = 'auth'

urlpatterns = [
    path('registration/', views.UserCreateView.as_view(), name='registration'),
    path('', include('django.contrib.auth.urls'), name='login'),
]
