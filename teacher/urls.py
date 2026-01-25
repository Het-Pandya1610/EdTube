from django.urls import path
from . import views

urlpatterns = [
    path('toggle-follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
]