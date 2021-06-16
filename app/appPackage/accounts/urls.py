from django.urls import path
from . import views

# used for namespacing applications
app_name = 'accounts'

# path: 4 args, first 2 required
# 1st: route = contains a URL pattern (localhost:8000/'route')
# 2nd: view = calls the matched specified function
# 3rd: kwargs = ?
# 4th: name = naming your urls lets you refer to it unambigiously from elsewehere in django (templates)
urlpatterns = [
    path("register", views.register, name='register'),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout")
]