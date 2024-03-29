from django.contrib import admin
from django.urls import path, include

from isucon.portal.contest.contact import views

urlpatterns = [
    path("", views.ticket_list, name="ticket_list"),
    path('ticket/<int:pk>/', views.ticket_detail, name="ticket_detail"),
    path('ticket/<int:pk>/close/', views.ticket_close, name="ticket_close"),
    path('new/', views.ticket_new, name="ticket_new"),
]
