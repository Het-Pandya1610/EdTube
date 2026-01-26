from django.urls import path
from . import views
from accounts.views import login_view, logout_view, register_view

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path('logout/', logout_view, name='logout'),
    path("verify-email/", views.reg, name="verify_email"),
    path("resend-otp/", views.resend_otp, name="resend_otp"),
    path("settings/",views.account_settings, name="account_settings"),
]
