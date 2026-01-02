from .forms import MyAuthForm
from django.contrib.auth.views import LoginView


class MyLoginView(LoginView):
    authentication_form = MyAuthForm
