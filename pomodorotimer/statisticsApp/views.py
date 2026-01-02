from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from .models import *


# TODO: Finish the function.
@login_required
def show_stats(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        userRecords = ActivityTime.objects.filter(owner=request.user.username)

        work_time_id = Activity.objects.filter(name='work').first().id
        work_time = userRecords.filter(activity_type=work_time_id)

        break_time_id = Activity.objects.filter(name='break').first().id
        break_time = userRecords.filter(activity_type=break_time_id)
        
        long_break_time_id = Activity.objects.filter(
            name='long_break').first().id
        long_break_time = userRecords.filter(activity_type=long_break_time_id)

        
        return
    return redirect('login')


# TODO: Add the function.
def show_timer(request: HttpRequest) -> HttpResponse:
    pass
