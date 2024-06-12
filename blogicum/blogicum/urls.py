from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('auth/', include('django.contrib.auth.urls'), name='login'),
    path('auth/', include('users.urls')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
]

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'

djdt = ['debug_toolbar', 'debug_toolbar.middleware.DebugToolbarMiddleware']

if (
    settings.DEBUG
    and djdt[0] in settings.INSTALLED_APPS
    and djdt[1] in settings.MIDDLEWARE
):
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
