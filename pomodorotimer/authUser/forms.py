from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django import forms
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=64,
    )

    username = forms.CharField(
        label=_("Username"),
        max_length=64,
    )

    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
    )

    password2 = forms.CharField(
        label=_("Password confirmation"),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = CustomUser
        fields = ("email", "username")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(_("A user with that email already exists."))
        return email


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'


class CustomAuthForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _(
            "Incorrect username or password. Note that both "
            "fields are case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }
