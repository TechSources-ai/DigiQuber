from django import forms
from .models import CustomUser

class SignupForm(forms.Form):
    email_or_phone = forms.CharField(label="Email or Phone", max_length=100)

    def clean_email_or_phone(self):
        value = self.cleaned_data.get('email_or_phone')
        if not value:
            raise forms.ValidationError("This field is required.")
        return value

class PasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'phone']  # Add more profile fields as needed

class SigninForm(forms.Form):
    email_or_phone = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)