from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.AboutPage.as_view(), name='about'),
    path('rules/', views.RulesPage.as_view(), name='rules'),

    # TODO: Удалить перед ревью
    # path('404.html/', views.page_not_found, name='page_not_found'),
]
