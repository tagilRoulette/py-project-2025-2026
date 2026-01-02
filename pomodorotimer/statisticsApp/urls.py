from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.show_stats),
]