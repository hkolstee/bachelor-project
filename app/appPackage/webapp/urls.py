from django.urls import path
from . import views
# from django.conf import settings
# from django.conf.urls.static import static

# used for namespacing applications
app_name = 'webapp'

# path: 4 args, first 2 required
# 1st: route = contains a URL pattern (localhost:8000/'route')
# 2nd: view = calls the matched specified function
# 3rd: kwargs = ?
# 4th: name = naming your urls lets you refer to it unambigiously from elsewehere in django (templates)
urlpatterns = [
    # /webapp
    # path('', views.index, name='index'),
    path('', views.IndexView.as_view(), name='index'),
    # /webapp/*detail*
    # path('<str:model_id>/', views.detail, name='detail')
    path('model/<str:pk>/', views.DetailView.as_view(), name='detail'),
    # /webapp/upload
    path('upload/', views.upload, name='upload')
]


# if settings.DEBUG:
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)