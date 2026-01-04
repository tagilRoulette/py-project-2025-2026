from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet, Case, When, Sum, Value, IntegerField
from django.db.models.functions import ExtractWeek, ExtractYear, ExtractMonth
from .models import *
from .forms import *
from matplotlib import pyplot
from datetime import date

ACTIVITIES = Activity.objects.values_list('name', flat=True)


@login_required
# TODO: Finish the function. Build the histogram.
def show_stats(request: HttpRequest) -> HttpResponse:

    def get_data_for_timespan(username: str,
                              aggregate_by: str = 'Daily',
                              start_date: date = date.today(),
                              end_date: date = date.today()) -> QuerySet:
        break_act_id_list = [
            Activity.objects.get(name='break').id,
            Activity.objects.get(name='long_break').id
        ]
        sum_expression = {
            'work': Sum(
                Case(
                    When(activity_type=Activity.objects.get(name='work').id,
                         then='time_span'),
                    default=Value(0),
                    output_field=IntegerField()
                )),
            'break': Sum(
                Case(
                    When(activity_type__in=break_act_id_list,
                         then='time_span'),
                    default=Value(0),
                    output_field=IntegerField()
                ))
        }
        user_records = ActivityTime.objects.filter(
            owner=username,
            date__range=(start_date, end_date))

        match aggregate_by:
            case 'Daily':
                user_records = (
                    user_records
                    .values('date')
                    .annotate(work_time=sum_expression['work'],
                              break_time=sum_expression['break'])
                )
            case 'Weekly':
                user_records = (
                    user_records
                    .annotate(
                        week=ExtractWeek('date'),
                        year=ExtractYear('date'),
                    )
                    .values('week', 'year')
                    .annotate(work_time=sum_expression['work'],
                              break_time=sum_expression['break'])
                )
            case 'Monthly':
                user_records = (
                    user_records
                    .annotate(
                        month=ExtractMonth('date'),
                        year=ExtractYear('date'),
                    )
                    .values('month', 'year')
                    .annotate(work_time=sum_expression['work'],
                              break_time=sum_expression['break'])
                )
            case _:
                raise ValueError('Wrong "aggregate_by" argument.')
        return user_records.order_by('date')

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
        if not form.is_valid():
            raise ValidationError('Form is not filled correctly.')
        time_span = form.cleaned_data['time_span']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        if time_span:
            user_records = get_data_for_timespan(
                request.user.username,
                time_span,
                start_date,
                end_date)
            # TODO: build histogram

        plot = pyplot.hist()

        return
    return redirect('login')


# TODO: Add the function.
def show_timer(request: HttpRequest) -> HttpResponse:
    pass
