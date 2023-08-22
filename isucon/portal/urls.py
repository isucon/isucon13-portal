"""portal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from isucon.portal import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.index, name='dashboard'),  # 暫定
    path('auth/', include("isucon.portal.authentication.urls")),
    # path('contest/', include("isucon.portal.contest.urls")),
    # path('internal/', include("isucon.portal.internal.urls")),
    path('admin/', admin.site.urls),
    path('', include('social_django.urls', namespace='social')),
]
