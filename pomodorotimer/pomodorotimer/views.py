from django.views import View
from .forms import *
from django.shortcuts import render, redirect
from statisticsApp.models import PomodoroTimings, ActivityTime
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


class AddTimeRecordsView(LoginRequiredMixin, View):
    template_name = 'manual_entry.html'

    def get(self, request, *args, **kwargs):
        form = ManualRecordEntryForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ManualRecordEntryForm(request.POST)
        if form.is_valid():
            ActivityTime.objects.create(
                owner=request.user,
                activity_type=form.cleaned_data['activity_type'],
                time_span=form.cleaned_data['time_span'],
                date=form.cleaned_data['date']
            )
            context = {'form': form,
                       'success_msg': 'Record saved.'}
            return render(request,
                          self.template_name,
                          context)
        return render(request,
                      self.template_name,
                      {'form': form})


@login_required
def change_pomodoro_timings(request: HttpRequest) -> HttpResponse:
    timings = PomodoroTimings.objects.get(request.user.username)
    if request.method == 'GET':
        context = {
            'work_time': timings.work_time,
            'break_time': timings.break_time,
            'long_break_time': timings.long_break_time
        }
        return render(request,
                      'change_timings.html',
                      context)
    form = ChangeTimingsForm(request.POST)
    if not form.is_valid():
        raise ValidationError('Form is not filled correctly.')
    timings.work_time = form.cleaned_data['work_time']
    timings.break_time = form.cleaned_data['break_time']
    timings.long_break_time = form.cleaned_data['long_break_time']
    context = {
        'work_time': timings.work_time,
        'break_time': timings.break_time,
        'long_break_time': timings.long_break_time
    }
    return render(request,
                  'change_timings.html',
                  context)
