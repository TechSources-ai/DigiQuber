from django.urls import path
from .views import buy_now_view, product_page_view

urlpatterns = [
    path('buy-now/', buy_now_view, name='buy_now'),
    path('product/', product_page_view, name='product_page'),
]