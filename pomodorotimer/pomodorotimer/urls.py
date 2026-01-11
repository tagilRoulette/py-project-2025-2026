from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authUser.urls')),
    path('', include('statisticsApp.urls')),
    path('', include('django.contrib.auth.urls')),
    path('timer/manual/', AddTimeRecordsView.as_view()),
    path('timings/', change_pomodoro_timings),
]
