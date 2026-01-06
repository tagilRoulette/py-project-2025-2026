from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from enum import StrEnum, auto


class DateAggInterval(StrEnum):
    Daily = auto()
    Weekly = auto()
    Monthly = auto()


class ChangeTimeSpanForm(forms.Form):
    preset_date_agg_interval = [
        (DateAggInterval.Daily, 'Daily'),
        (DateAggInterval.Weekly, 'Weekly'),
        (DateAggInterval.Monthly, 'Monthly'),
    ]
    date_agg_interval = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=preset_date_agg_interval,
    )

    input_time_formats = [
        r'%d/%m/%Y',
        r'%d.%m.%Y',
        r'%d-%m-%Y'
    ]
    start_date = forms.DateField(
        input_formats=input_time_formats, required=False)
    end_date = forms.DateField(
        input_formats=input_time_formats, required=False)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # has_full_dates = start_date and end_date
        # if has_full_dates:
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = date.today()
        if end_date < start_date:
            raise ValidationError({
                'end_date': 'Дата окончания не может быть раньше даты начала'
            })
        #     cleaned_data['date_agg_interval'] = None
        # else:
        #     cleaned_data['start_date'] = None
        #     cleaned_data['end_date'] = None
            # today = date.today()
            # match cleaned_data.get('date_agg_interval'):
            #     case 'Today':
            #         start_date = today
            #         end_date = today
            #     case 'Week':
            #         days_to_monday = today.weekday()
            #         monday_date = today - timedelta(days=days_to_monday)
            #         sunday_date = monday_date + timedelta(days=7)
            #         start_date = monday_date
            #         end_date = sunday_date
            #     case 'Month':
            #         month_start = today.

        return cleaned_data
