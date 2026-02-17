from django.urls import path
from . import views

urlpatterns = [
    path("upload/",views.videoUpload,name="videoUpload"),
    path('watch', views.watchVideo, name='watch_video'),
    path('history/', views.videoHistory, name="vidhistory"),
    path('quiz/', views.quiz, name='quiz'),
    path("like/<str:video_id>/",views.toggle_video_like,name="toggle_video_like"),
]
