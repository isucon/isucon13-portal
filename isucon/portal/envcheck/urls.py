from django.urls import path
from isucon.portal.envcheck import views

app_name = 'envcheck'

urlpatterns = [
    path('info/', views.get_info, name="get_info"),
    path('result/', views.save_result, name="save_result"),
]
