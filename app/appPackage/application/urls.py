"""application URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path


# path: 4 args, first 2 required
# 1st: route = contains a URL pattern (localhost:8000/'route')
# 2nd: view = calls the matched specified function
# 3rd: kwargs = ?
# 4th: name = naming your urls lets you refer to it unambigiously from elsewehere in django (templates)
urlpatterns = [
    path('webapp/', include('webapp.urls')),
    path('admin/', admin.site.urls),
]
