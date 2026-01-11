from .forms import CustomAuthForm, CustomUserCreationForm
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView
from statisticsApp.models import PomodoroTimings
from django.contrib.auth import login, authenticate


class MyLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = CustomAuthForm


class MyUserCreationView(CreateView):
    template_name = 'signup.html'
    success_url = '/stats/'
    form_class = CustomUserCreationForm

    def form_valid(self, form):
        result = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')

        user = authenticate(username=username,
                            password=password)
        if user is not None:
            login(self.request, user)
            PomodoroTimings.objects.create(owner=user)
        return result
