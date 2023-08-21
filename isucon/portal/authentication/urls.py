from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from isucon.portal.authentication import views

urlpatterns = [
    path('login/', views.LoginView.as_view(template_name="login.html"), name="login"),
    path('logout/', auth_views.LogoutView.as_view(template_name="logout.html"), name="logout"),
    path('create_team/', views.create_team, name="create_team"),
    path('join_team/', views.join_team, name="join_team"),
    path('teams/', views.team_list, name="team_list"),
    path('teams.csv', views.team_list_csv, name="team_list_csv"),
    path('settings/team/', views.team_settings, name="team_settings"),
    path('settings/icon/', views.update_user_icon, name="update_user_icon"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL)
