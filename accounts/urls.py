from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.reg, name="reg"),
    path("login/", views.login_view, name="login"),
    path("verify-email/", views.reg, name="verify_email"),
    path("resend-otp/", views.resend_otp, name="resend_otp"),
    path("settings/",views.account_settings, name="account_settings"),
]
