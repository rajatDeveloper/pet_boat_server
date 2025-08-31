
from django.urls import path , include
from userApp.api.views import (
    regisgration_view,
    logout_view,
    login_with_email,
    user_addresses,
)

urlpatterns = [
    path('login-email/' , login_with_email , name='login-email'),
    path('register/' , regisgration_view , name='register') , 
    path('logout/' , logout_view , name='logout'),
    path('users/<int:user_id>/addresses/', user_addresses, name='user-addresses'),
]