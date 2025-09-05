# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('createCustomer/', views.createCustomerView, name='createCustomer'),
    path('create-profile/<str:user_id>/', views.createProfileView, name='create_profile'),
]
