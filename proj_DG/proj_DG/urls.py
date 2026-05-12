from django.contrib import admin
from django.urls import path, include

# handler429 = 'proj_DG.views.ratelimited_error'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_login.urls')),
    path('app_user/', include('app_user.urls')),
    path('app_shop/', include('app_shop.urls')),
    path('app_admin/', include('app_admin.urls')),
    path('app_trade/', include('app_trade.urls')),
    path('payments/', include('app_pay.urls')),
    path("sell/", include("app_sell.urls")),
    path("", include("app_sell.urls"))

]
