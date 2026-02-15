from django.urls import path
from . import views
from accounts.views import login_view, logout_view, register_view

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path('logout/', logout_view, name='logout'),
    path("verify-email/", views.reg, name="verify_email"),
    path("resend-otp/", views.resend_otp, name="resend_otp"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("verify-reset-otp/", views.verify_reset_otp, name="verify_reset_otp"),
    path("set-new-password/", views.set_new_password, name="set_new_password"),
    path("settings/",views.account_settings, name="account_settings"),
    path("advanced-settings/", views.advanced_settings, name="advanced_settings"),
    path("update-username/", views.update_username, name="update_username"),
    path("update-name-appearance/", views.update_name_appearance, name="update_name_appearance"),
    path("update-teacher-info/", views.update_teacher_info, name="update_teacher_info"),
    path("check-username/", views.check_username, name="check_username"),
    path("suggest-usernames/", views.suggest_usernames, name="suggest_usernames"),
    path("get-name-preview/", views.get_name_preview, name="get_name_preview"),
    path("upgrade-to-teacher/", views.upgrade_to_teacher, name="upgrade_to_teacher"),
    path("delete-account/", views.delete_account, name="delete_account"),
]
