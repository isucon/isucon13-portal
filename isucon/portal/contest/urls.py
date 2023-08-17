from django.contrib import admin
from django.urls import path, include

from isucon.portal.contest import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('jobs/', views.jobs, name="jobs"),
    path('jobs/enqueue/', views.job_enqueue, name="job_enqueue"),
    path('jobs/<int:pk>/', views.job_detail, name="job_detail"),
    path('scores/', views.scores, name="scores"),
    path('servers/', views.servers, name="servers"),
    path('servers/<int:pk>/', views.delete_server, name="delete_server"),
    path('graph/', views.graph, name="graph"),
    path('teams/', views.teams, name="teams"),
    path('staff/', include("isucon.portal.contest.staff.urls")),
    path('result/', include("isucon.portal.contest.result.urls")),
]
