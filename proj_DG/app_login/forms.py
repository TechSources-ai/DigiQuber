from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser
import re


# =========================
# Shared validation mixin
# =========================
class EmailOrPhoneMixin(forms.Form):
    email_or_phone = forms.CharField(label="Email or Phone", max_length=100)

    def clean_email_or_phone(self):
        value = self.cleaned_data.get("email_or_phone", "").strip()

        if not value:
            raise forms.ValidationError("This field is required.")

        # Phone validation
        if value.isdigit():
            if len(value) < 10:
                raise forms.ValidationError("Invalid phone number")
            return value

        # Email validation
        email_regex = r"^[^@]+@[^@]+\.[^@]+$"
        if not re.match(email_regex, value):
            raise forms.ValidationError("Invalid email address")

        return value


# =========================
# Signup (Email / Phone)
# =========================
class SignupForm(EmailOrPhoneMixin):
    pass


# =========================
# Password Creation
# =========================
class PasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput,
        strip=False,
        label="Password"
    )

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password


# =========================
# Profile Completion (Onboarding only)
# =========================
class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["email", "phone"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Email already in use.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone and CustomUser.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Phone already in use.")
        return phone


# =========================
# Sign In
# =========================
class SigninForm(EmailOrPhoneMixin):
    password = forms.CharField(
        widget=forms.PasswordInput,
        strip=False,
        label="Password"
    )


# =========================
# Email Confirmation (Token)
# =========================
class EmailTokenConfirmForm(forms.Form):
    email = forms.EmailField(label="Email")
    token = forms.CharField(
        max_length=6,
        min_length=6,
        label="Verification Code"
    )


# =========================
# Phone Confirmation (OTP)
# =========================
class PhoneOTPConfirmForm(forms.Form):
    phone = forms.CharField(max_length=15)
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        label="OTP"
    )

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone.isdigit() or len(phone) < 10:
            raise forms.ValidationError("Invalid phone number")
        return phone
