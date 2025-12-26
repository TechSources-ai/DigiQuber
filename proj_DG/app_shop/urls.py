from django.urls import path
from . import views 
from .views import balance_page

urlpatterns = [
    path('chk_price/', views.chk_price_view, name='chk_price'),
    path('inquiry/<str:param1>/', views.tradeEstimateView, name='inquiry'),
    path('product/', views.product_page_view, name='product_page'),
    #path('balance/', views.customer_detail, name='balance'),
    path('refresh_balance/', views.refresh_balance, name='refresh_balance'),
    #path("balance/", balance_page, name="balance_page"),
    path('balance/', views.balance_page, name='balance'),
    #path('inquiry/<str:param1>/', views.generate_quote, name='inquiry')
    path('buy-gold/', views.chk_price_view, name='buy_gold'),
    path('buy-silver/', views.chk_price_view, name='buy_silver'),
    path("live-prices/", views.live_prices, name="live_prices"),



]