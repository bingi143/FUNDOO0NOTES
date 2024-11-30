from django.urls import path
from . import views
from .views import RegistrationUser, LoginUser,verify_email


urlpatterns = [
    path('register/', RegistrationUser.as_view(), name='register_user'),
    path('email_verify/<str:token>/',verify_email,name='verify_email'),
    path('login/', LoginUser.as_view(), name='login_user'),
]
