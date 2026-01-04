from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet, Sum, Value
from .models import *
from .forms import *
from matplotlib import pyplot
from datetime import date

ACTIVITIES = Activity.objects.values_list('name', flat=True)


@login_required
# TODO: Finish the function.
def show_stats(request: HttpRequest) -> HttpResponse:
    def get_data_for_timespan(username: str, 
                              aggregate_by: str,
                              start_date: date = date.today(),
                              end_date: date = date.today()) -> QuerySet:
        user_records = ActivityTime.objects.filter(
            owner=username,
            date__date__range=(start_date, end_date))
        match aggregate_by:
            case 'Daily':
                user_records.values(days=Value('date__day'))  # TODO: incorrect. see notes.
            case 'Weekly':
                pass
            case 'Monthly':
                pass
        return 

    def get_data_for_month(username: str,
                           month: int) -> QuerySet:
        return (ActivityTime.objects.filter(
            owner=username,
            date__month=month)
            .aggregate())

    def get_activity_time(activity_name: str,
                          user_records: QuerySet) -> QuerySet:
        activity_name = activity_name.lower()
        if activity_name not in ACTIVITIES:
            raise ValueError(
                'The activity name is not in the activities list.')
        activity_id = Activity.objects.get(name=activity_name).id
        # activity_id = Activity.objects.filter(name=activity_name).first().id
        return user_records.filter(activity_type=activity_id)

    if request.user.is_authenticated:
        if request.method == 'GET':
            user_records = get_data_for_timespan(request.user.username)

            return render(request, 'stats.html', {'stats_form': ChangeTimeSpanForm})
        form = ChangeTimeSpanForm(request.POST)
        time_span = form.cleaned_data['time_span']
        user_records = QuerySet()
        if time_span:
            today = date.today()
            match time_span:
                case 'Daily':
                    user_records = get_data_for_timespan(request.user.username)
                    # TODO: build histogram
                    # return render(get_data_for_timespan(request.user.username), 'stats.html', {'stats_form': ChangeTimeSpanForm, 'stats': })
                case 'Weekly':
                    days_to_monday = today.weekday()
                    monday_date = today - timedelta(days=days_to_monday)
                    sunday_date = monday_date + timedelta(days=7)
                    user_records = get_data_for_timespan(
                        request.user.username, monday_date, sunday_date)
                    # TODO: build histogram
                case 'Monthly':
                    user_records = get_data_for_month(
                        request.user.username, date.month)
                    # TODO: build histogram

        # userRecords = ActivityTime.objects.filter(owner=request.user.username)

        # work_time_id = Activity.objects.filter(name='work').first().id
        # work_time = userRecords.filter(activity_type=work_time_id)

        # break_time_id = Activity.objects.filter(name='break').first().id
        # break_time = userRecords.filter(activity_type=break_time_id)

        # long_break_time_id = Activity.objects.filter(
        #     name='long_break').first().id
        # long_break_time = userRecords.filter(activity_type=long_break_time_id)

        plot = pyplot.hist()

        return
    return redirect('login')


# TODO: Add the function.
def show_timer(request: HttpRequest) -> HttpResponse:
    pass
