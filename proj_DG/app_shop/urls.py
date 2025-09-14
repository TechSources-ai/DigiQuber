from django.urls import path
from .views import buy_now_view, product_page_view, customer_detail, refresh_balance

urlpatterns = [
    path('buy-now/', buy_now_view, name='buy_now'),
    path('product/', product_page_view, name='product_page'),
    path('balance/', customer_detail, name='balance'),
    path('balance/', refresh_balance, name='refresh_balance'),
]