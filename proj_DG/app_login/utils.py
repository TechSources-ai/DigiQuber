# from django.conf import settings
# from django.core.mail import send_mail

# def send_confirmation_email(email, token):
#     link = f"http://localhost:8000/confirm-email/?token={token}"
#     send_mail(
#         'Confirm your email',
#         f'Click the link to confirm your email: {link}',
#         settings.DEFAULT_FROM_EMAIL,
#         [email],
#         fail_silently=False,
#     )

# def send_otp(phone, otp):
#     # Implement SMS sending logic here (use a service like Twilio)
#     print(f"Send OTP {otp} to phone {phone}")


import os
import logging
from azure.communication.email import EmailClient
from django.conf import settings

logger = logging.getLogger(__name__)


def send_confirmation_email(toaddr: str, msg: str) -> bool:
    """
    Sends email via Azure Communication Services
    Returns True on success, False on failure
    """
    try:
        connection_string = os.getenv("AZURE_EMAIL_CONNECTION_STRING")
        sender = os.getenv("AZURE_EMAIL_SENDER")

        if not connection_string:
            raise ValueError("AZURE_EMAIL_CONNECTION_STRING not set")

        if not sender:
            raise ValueError("AZURE_EMAIL_SENDER not set")

        client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": sender,
            "recipients": {
                "to": [{"address": toaddr}]
            },
            "content": {
                "subject": "Login OTP",
                "plainText": msg,
                "html": f"<p>{msg}</p>",
            },
        }

        poller = client.begin_send(message)
        result = poller.result()

        logger.info(f"Email sent to {toaddr}, result={result}")
        return True

    except Exception as ex:
        logger.error(f"Azure Email error: {ex}", exc_info=True)
        return False


def send_otp(phone: str, otp: str):
    """
    Placeholder for SMS OTP (Twilio / Azure SMS later)
    """
    logger.info(f"Send OTP {otp} to phone {phone}")
