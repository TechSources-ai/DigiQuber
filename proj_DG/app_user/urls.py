from django.urls import path
from .views import edit_profile_view

urlpatterns = [
    path('edit-profile/', edit_profile_view, name='edit_profile'),
]