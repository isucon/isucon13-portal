from django.contrib import admin
from django.urls import path, include

from isucon.portal.contest import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('cloudformation_contest.yaml', views.cloudformation_contest, name="cloudformation_contest"),
    path('jobs/', views.jobs, name="jobs"),
    path('jobs/enqueue/', views.job_enqueue, name="job_enqueue"),
    path('jobs/<int:pk>/', views.job_detail, name="job_detail"),
    path('scores/', views.scores, name="scores"),
    path('servers/', views.servers, name="servers"),
    # path('graph/', views.graph, name="graph"),
    # path('teams/', views.teams, name="teams"),
    # path('staff/', include("isucon.portal.contest.staff.urls")),
    # path('result/', include("isucon.portal.contest.result.urls")),
]
