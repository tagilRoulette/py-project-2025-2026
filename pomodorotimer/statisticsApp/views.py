from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet, Case, When, Sum, Value, IntegerField
from django.db.models.functions import ExtractWeek, ExtractYear, ExtractMonth
from .models import *
from .forms import *
import numpy as np
from matplotlib import pyplot
from datetime import date
from io import StringIO, BytesIO

ACTIVITIES = Activity.objects.values_list('name', flat=True)
TIME_FORMAT = r'%d.%m.%Y'
GRAPH_BAR_SPACING = 0.5


@login_required
# TODO: Finish the function. Build the histogram.
def show_stats(request: HttpRequest) -> HttpResponse:

    # TODO: move the function to model?
    def get_data_for_timespan(username: str,
                              start_date: date,
                              end_date: date,
                              aggregate_by=DateAggInterval.Daily,
                              ) -> QuerySet:
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
            case DateAggInterval.Daily:
                user_records = (
                    user_records
                    .values('date')
                    .annotate(work_time=sum_expression['work'],
                              break_time=sum_expression['break'])
                )
            case DateAggInterval.Weekly:
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
            case DateAggInterval.Monthly:
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

    def build_bars_graph(values_dicts: list[dict],
                         bar_spacing: float):
        # fig = pyplot.subplots(figsize=(12, 8))

        bars = []
        for day_index, day_data in enumerate(values_dicts):
            if day_index == 0:
                bars.append(np.arange(len(values_dicts)))
            else:
                bars.append(
                    [x_coord + bar_spacing
                     for x_coord in bars[day_index - 1]])

            # TODO: sometimes v is int (e.g., month, week), sometimes is a date. need to 
            # unify the process logic to later label values on plot w/ date_str
            date_data = tuple(v.strftime(TIME_FORMAT) 
                              for k, v in day_data.items()
                              if k not in ('work', 'break'))
            date_str = ' - '.join(date_data)
            day_data = (day_data['work'], day_data['break'])
            pyplot.bar(
                bars[day_index],
                day_data,
                width=bar_spacing,
                label=date_str)
        # for value_index, value in values:
        #     if value_index == 0:
        #         bars.append(np.arange(len(value)))
        #     else:
        #         bars.append(
        #             [x_value + bar_spacing for x_value in bars[value_index - 1]])
        #     pyplot.bar(bars[value_index], value,
        #                width=bar_spacing, label=values_names[value_index])
        pyplot.legend()

        # TODO: string argument expected, got 'bytes'. see into the problem
        # img = BytesIO()
        img = StringIO()
        pyplot.figure().savefig(img, format='jpeg')
        img.seek(0)
        return img.getvalue()

    def form_response_context(stats_graph: str,
                              start_date: date,
                              end_date: date,
                              agg_interval,
                              **kwargs) -> dict:
        context = {'stats_graph': stats_graph,
                   'stats_form': ChangeTimeSpanForm}
        start_date = start_date.strftime(TIME_FORMAT)
        end_date = end_date.strftime(TIME_FORMAT)
        if start_date == end_date:
            context['stats_period_info'] = start_date
        else:
            context['stats_period_info'] = f'{start_date} - {end_date} {agg_interval}'
        context.update(kwargs)
        return context

    def correct_agg_time_period(start_date: date,
                                end_date: date,
                                agg_period):
        match agg_period:
            case DateAggInterval.Daily:
                return agg_period
            case DateAggInterval.Weekly:
                start_date_week = start_date.isocalendar()[1]
                end_date_week = end_date.isocalendar()[1]

                if (start_date_week == end_date_week
                        and start_date.year == end_date.year):
                    return DateAggInterval.Daily
                return agg_period
            case DateAggInterval.Monthly:
                if (start_date.month == end_date.month
                        and start_date.year == end_date.year):
                    return correct_agg_time_period(start_date,
                                                   end_date,
                                                   DateAggInterval.Weekly)
                return agg_period

    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'GET':
        start_date = end_date = date.today()
        user_records = get_data_for_timespan(request.user.username,
                                             start_date,
                                             end_date)
        graph = build_bars_graph(user_records,
                                 GRAPH_BAR_SPACING)
        context = form_response_context(graph,
                                        start_date,
                                        end_date,
                                        DateAggInterval.Daily)
        return render(request,
                      'stats.html',
                      context)

    form = ChangeTimeSpanForm(request.POST)
    if not form.is_valid():
        raise ValidationError('Form is not filled correctly.')

    start_date = form.cleaned_data['start_date']
    end_date = form.cleaned_data['end_date']
    date_agg_interval = correct_agg_time_period(start_date,
                                                end_date,
                                                form.cleaned_data['date_agg_interval'])

    user_records = get_data_for_timespan(request.user.username,
                                         start_date,
                                         end_date,
                                         date_agg_interval)
    graph = build_bars_graph(user_records, GRAPH_BAR_SPACING)
    context = form_response_context(graph,
                                    start_date,
                                    end_date,
                                    date_agg_interval)
    return render(request,
                  'stats.html',
                  context)


# TODO: Add the function.
def show_timer(request: HttpRequest) -> HttpResponse:
    pass
