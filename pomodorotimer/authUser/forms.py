from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django import forms
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=("Email"),
        max_length=64,
    )

    username = forms.CharField(
        label=("Username"),
        max_length=64,
    )

    password1 = forms.CharField(
        label=("Password"),
        strip=False,
        widget=forms.PasswordInput,
    )

    password2 = forms.CharField(
        label=("Password confirmation"),
        strip=False,
        help_text=("Enter the same password as before, for verification."),
        widget=forms.PasswordInput,
    )

    class Meta:
        model = CustomUser
        fields = ("email", "username")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(("A user with that email already exists."))
        return email


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'


class CustomAuthForm(AuthenticationForm):
    error_messages = {
        'invalid_login': (
            "Incorrect username or password. Note that both "
            "fields are case-sensitive."
        ),
        'inactive': ("This account is inactive."),
    }
