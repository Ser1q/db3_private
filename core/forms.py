from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import AppUser


class AppUserForm(forms.ModelForm):
    class Meta:
        model = AppUser
        fields = ["given_name", "surname", "email", "password", "city", "phone_number"]
        widgets = {
            "password": forms.PasswordInput(render_value=True),
        }


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput())


class CaregiverRegistrationForm(forms.Form):
    given_name = forms.CharField(max_length=50)
    surname = forms.CharField(max_length=50)
    email = forms.EmailField()
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)
    city = forms.CharField(max_length=50)
    phone_number = forms.CharField(max_length=20, required=False)
    caregiving_type = forms.ChoiceField(
        choices=[
            ("Babysitter", "Babysitter"),
            ("Elderly Care", "Elderly Care"),
            ("Playmate for children", "Playmate for children"),
        ]
    )
    gender = forms.ChoiceField(
        choices=[("M", "Male"), ("F", "Female"), ("Other", "Other")], required=False
    )
    hourly_rate = forms.DecimalField(max_digits=10, decimal_places=2)
    profile_description = forms.CharField(widget=forms.Textarea, required=False)
    photo = forms.FileField(label="Photo (upload)", required=False)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "Passwords do not match.")
        return cleaned


class MemberRegistrationForm(forms.Form):
    given_name = forms.CharField(max_length=50)
    surname = forms.CharField(max_length=50)
    email = forms.EmailField()
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)
    city = forms.CharField(max_length=50)
    phone_number = forms.CharField(max_length=20, required=False)
    house_number = forms.CharField(max_length=20, required=False)
    street = forms.CharField(max_length=100, required=False)
    town = forms.CharField(max_length=50, required=False)
    house_rules = forms.CharField(widget=forms.Textarea, required=False)
    dependent_description = forms.CharField(widget=forms.Textarea, required=False)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "Passwords do not match.")
        return cleaned


class JobForm(forms.Form):
    required_caregiving_type = forms.ChoiceField(
        choices=[
            ("Babysitter", "Babysitter"),
            ("Elderly Care", "Elderly Care"),
            ("Playmate for children", "Playmate for children"),
        ]
    )
    other_requirements = forms.CharField(widget=forms.Textarea, required=False)
