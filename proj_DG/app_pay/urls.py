# from django.urls import path
# from . import views
# from .views import payment_page, create_order, payment_success, razorpay_webhook

# urlpatterns = [
#     path('payment/', views.payment_page, name='payment_page'),          # GET -> show payment / create order
#     path('create-order/', views.create_order, name='create_order'),    # POST -> create razorpay order if using ajax
#     path('webhook/', views.razorpay_webhook, name='razorpay_webhook'), # POST -> verify webhook
#     path('success/', views.payment_success, name='payment_success'),
# ]


# app_pay/urls.py

from django.urls import path
from .views import payment_page, create_order, payment_success, razorpay_webhook

urlpatterns = [
    path('payment/', payment_page, name='payment_page'),           # ← CHANGED: pay/ → payment/
    path('create-order/', create_order, name='create_order'),      # ← keep this
    path('success/', payment_success, name='payment_success'),    # ← keep this
    path('webhook/', razorpay_webhook, name='razorpay_webhook'),   # ← keep this
]