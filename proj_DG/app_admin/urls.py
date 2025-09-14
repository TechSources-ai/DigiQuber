# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('createCustomer/', views.createCustomerView, name='createCustomer'),
    path('create-profile/<str:user_id>/', views.createProfileView, name='create_profile'),
    path('fetch-profile/<str:user_id>/', views.fetchProfileView, name='fetch_profile'),
    path('forceUpdate/', views.updateDgCustId, name='update'),
]
