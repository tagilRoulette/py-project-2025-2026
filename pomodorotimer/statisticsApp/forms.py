from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta


class ChangeTimeSpanForm(forms.Form):
    preset_time_span = [
        ('1', 'Daily'),
        ('2', 'Weekly'),
        ('3', 'Monthly'),
    ]
    time_span = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=preset_time_span,
    )
    start_date = forms.DateField(
        input_formats=[r'%d/%m/%Y'], required=False)
    end_date = forms.DateField(
        input_formats=[r'%d/%m/%Y'], required=False)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # has_full_dates = start_date and end_date
        # if has_full_dates:
        if end_date < start_date:
            raise ValidationError({
                'end_date': 'Дата окончания не может быть раньше даты начала'
            })
        #     cleaned_data['time_span'] = None
        # else:
        #     cleaned_data['start_date'] = None
        #     cleaned_data['end_date'] = None
            # today = date.today()
            # match cleaned_data.get('time_span'):
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
