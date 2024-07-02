from django.urls import include, path

from . import views


urlpatterns = [
    path('', include('django.contrib.auth.urls'), name='login'),
    path('registration/', views.UserCreateView.as_view(), name='registration'),
]
