from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.about, name='about'),
    path('rules/', views.rules, name='rules'),
    # TODO: Удалить перед ревью
    # path('404.html/', views.page_not_found, name='page_not_found'),
]
