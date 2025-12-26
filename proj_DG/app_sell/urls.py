from django.urls import path,include
from .views import sell_quote_view, sell_confirm_view,sell_page_view,sell_page_view

urlpatterns = [
    #path("get-quote/", views.get_quote, name="sell_get_quote"),
    #path("execute/", views.execute_sell, name="sell_execute"),
    #path("get-session/", views.get_session, name="sell_get_session"),
    path("sell/", sell_page_view, name="sell_page"),
    path("sell/quote/", sell_quote_view, name="sell_quote"),
    path("sell/confirm/", sell_confirm_view, name="sell_confirm"),
    #path("sell/success/", sell_success_view, name="sell_success"),


]
