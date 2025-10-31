from django.urls import path
from . import views 

urlpatterns = [
    path('chk_price/', views.chk_price_view, name='chk_price'),
    path('inquiry/<str:param1>/', views.tradeEstimateView, name='inquiry'),
    path('product/', views.product_page_view, name='product_page'),
    path('balance/', views.customer_detail, name='balance'),
    path('refresh_balance/', views.refresh_balance, name='refresh_balance'),
]