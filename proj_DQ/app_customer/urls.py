from django.urls import path
from . import views

urlpatterns = [
    path('', views.email_entry_view, name='email_entry'),
    path('authe/', views.authenticate_with_api, name='authe'),
    path('create/', views.create_customer, name='create'),
    path('confirm/', views.confirm_email_view, name='confirm_email'),
    # path('profile/', views.create_profile_view, name='create_profile'),
    path('profile/', views.create_profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]

# # app_customer/urls.py
# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.email_entry_view, name='email_entry'),
#     path('confirm/', views.confirm_email_view, name='confirm_email'),
#     path('profile/', views.create_profile_view, name='create_profile'),
#     path('dashboard/', views.dashboard_view, name='dashboard'),
# ]
