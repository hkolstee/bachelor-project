from django.urls import path
from . import views

# used for namespacing applications
app_name = 'webapp'

# path: 4 args, first 2 required
# 1st: route = contains a URL pattern (localhost:8000/'route')
# 2nd: view = calls the matched specified function
# 3rd: kwargs = ?
# 4th: name = naming your urls lets you refer to it unambigiously from elsewehere in django (templates)
urlpatterns = [
    # /webapp
    path('', views.IndexView.as_view(), name='index'),
    # /webapp/*detail*
    path('model/<str:pk>/', views.DetailView.as_view(), name='detail'),
    # /webapp/upload
    path('upload/', views.UploadView.as_view(), name='upload'),
    path('files/', views.FileListView.as_view(), name='file_list'),
    path('files/<int:pk>/', views.delete_file, name='delete_file'),
    path('model/deleteanno/<int:pk>/', views.delete_anno, name='delete_anno'),
    path('model/<int:pk>/updatedesc/', views.UpdateDescView.as_view(), name='updatedesc'),
    path('model/<int:pk>/updateanno/', views.UpdateAnnoView.as_view(), name='updateanno'),
    path('model/<int:pk>/createanno/', views.CreateAnnoView.as_view(), name='createanno'),
    # For accounts 
    path("register", views.register, name='register'),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
]