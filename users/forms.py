from django import forms
from django.contrib.auth.forms import UserCreationForm
from . import models


class RegistrationTypeForm(forms.Form):
    choices = [
        ("in", "individual"),
        ("co", "organization")
    ]
    account_type = forms.ChoiceField(
        widget=forms.RadioSelect(), choices=choices)


class UserRegistrationForm(UserCreationForm):
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = models.CustomUser
        fields = ['email', 'password1', 'password2']

    def clean_honeypot(self):
        if self.cleaned_data['honeypot']:
            raise forms.ValidationError("Spam detected.")
        return self.cleaned_data['honeypot']


class IndividualProfileRegistrationForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ['first_name', 'last_name', 'organization']


class OrganizationProfileRegistrationForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ['first_name', 'last_name']


class OrganizationRegistrationForm(forms.ModelForm):
    class Meta:
        model = models.Organization
        fields = ['name', 'entity_type']  # Add other organization fields


class OrganizationAddUserForm(forms.Form):
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput())
    email = forms.EmailField(required=True)

    def clean_honeypot(self):
        if self.cleaned_data['honeypot']:
            raise forms.ValidationError("Spam detected.")
        return self.cleaned_data['honeypot']


class LoginForm(forms.Form):
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput)


class ResendVerificationEmailForm(forms.Form):
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)
    email = forms.EmailField(required=True)


class PasswordResetForm(forms.Form):
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)
    email = forms.EmailField(required=True)
