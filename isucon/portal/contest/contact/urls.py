from django.contrib import admin
from django.urls import path, include

from isucon.portal.contest.contact import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
]
