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
    # /index
    # path('', views.index, name='index'),
    path('', views.IndexView.as_view(), name='index'),
    # /
    # path('<str:model_id>/', views.detail, name='detail')
    path('<str:pk>/', views.DetailView.as_view(), name='detail')
    
]