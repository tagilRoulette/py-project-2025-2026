from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page),
    path('stats/', views.show_stats),
]
