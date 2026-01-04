from .forms import CustomAuthForm
from django.contrib.auth.views import LoginView


class MyLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = CustomAuthForm
