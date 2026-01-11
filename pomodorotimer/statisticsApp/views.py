from matplotlib import pyplot
from io import StringIO
from datetime import date
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet, Case, When, Sum, Value, IntegerField
from django.db.models.functions import ExtractWeek, ExtractYear, ExtractMonth
from .models import *
from .forms import *
import numpy as np
import matplotlib
matplotlib.use('Agg')


ACTIVITIES = Activity.objects.values_list('name', flat=True)
TIME_FORMAT = r'%d.%m.%Y'
GRAPH_BAR_SPACING = 0.15
GRAPH_BAR_WIDTH = 0.15


@login_required
def show_stats(request: HttpRequest) -> HttpResponse:
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
        return user_records

    def build_bars_graph(values_dicts: list[dict],
                         bar_spacing: float,
                         bar_width: float):
        bars = []
        dates = []
        work_time = [timespan_data['work_time']
                     for timespan_data in values_dicts]
        break_time = [timespan_data['break_time']
                      for timespan_data in values_dicts]
        for timespan_index, timespan_data in enumerate(values_dicts):
            if timespan_index == 0:
                bars.append(np.arange(len(values_dicts)))
            else:
                bars.append([x_coord + bar_spacing
                             for x_coord in bars[timespan_index - 1]])

            date_data = tuple(v
                              for k, v in timespan_data.items()
                              if k not in ('work_time', 'break_time'))
            date_data = tuple(d.strftime(TIME_FORMAT)
                              if isinstance(d, date)
                              else str(d)
                              for d in date_data)
            dates.append(' - '.join(date_data))

        if not bars:
            return 'No data.'
        if len(bars) == 1:
            pyplot.bar(bars[0] + 0.08,
                       work_time,
                       bar_width,
                       label='Work time')
            pyplot.bar(bars[0] - 0.08,
                       break_time,
                       bar_width,
                       label='Break time')
            pyplot.xticks(bars[0], dates)
        else:
            pyplot.bar([bar - 0.08 for bar in bars[1]],
                       work_time,
                       bar_width,
                       label='Work time')
            pyplot.bar([bar + 0.08 for bar in bars[1]],
                       break_time,
                       bar_width,
                       label='Break time')
            pyplot.xticks(bars[1], dates)
        pyplot.legend()

        img = StringIO()
        pyplot.savefig(img, format='svg')
        pyplot.close()
        img.seek(0)
        return img.getvalue()

    def form_response_context(stats_graph: bytes,
                              start_date: date,
                              end_date: date,
                              username: str,
                              agg_interval) -> dict:
        context = {'stats_graph': stats_graph,
                   'stats_form': ChangeTimeSpanForm,
                   'username': username}
        start_date = start_date.strftime(TIME_FORMAT)
        end_date = end_date.strftime(TIME_FORMAT)
        if start_date == end_date:
            context['stats_period_info'] = start_date
        else:
            context['stats_period_info'] = f'{start_date} - {end_date} {agg_interval}'
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

    if request.method == 'GET':
        start_date = end_date = date.today()
        user_records = get_data_for_timespan(request.user.username,
                                             start_date,
                                             end_date)
        graph = build_bars_graph(user_records,
                                 GRAPH_BAR_SPACING,
                                 GRAPH_BAR_WIDTH)
        context = form_response_context(graph,
                                        start_date,
                                        end_date,
                                        request.user.username,
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
    graph = build_bars_graph(user_records,
                             GRAPH_BAR_SPACING,
                             GRAPH_BAR_WIDTH)
    context = form_response_context(graph,
                                    start_date,
                                    end_date,
                                    request.user.username,
                                    date_agg_interval)
    return render(request,
                  'stats.html',
                  context)

def main_page(request):
    return redirect('stats/')

# TODO: Add the function.
def show_timer(request: HttpRequest) -> HttpResponse:
    pass
