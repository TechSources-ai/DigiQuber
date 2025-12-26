from django.conf import settings
from django.core.mail import send_mail

def send_confirmation_email(email, token):
    link = f"http://localhost:8000/confirm-email/?token={token}"
    send_mail(
        'Confirm your email',
        f'Click the link to confirm your email: {link}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )

def send_otp(phone, otp):
    # Implement SMS sending logic here (use a service like Twilio)
    print(f"Send OTP {otp} to phone {phone}")