from django.urls import path
from . import views

urlpatterns = [
    path("upload/",views.videoUpload,name="videoUpload"),
    path('watch', views.watchVideo, name='watch_video'),
    path('history/', views.videoHistory, name="video_history"),
    path("quiz/<str:quiz_id>/", views.quiz, name="quiz"),
    path('quiz/<str:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path("like/<str:video_id>/",views.toggle_video_like,name="toggle_video_like"),
    path('edit/<str:video_id>/', views.edit_video, name='edit_video'),
    path('delete/<str:video_id>/', views.delete_video, name='delete_video'),
    path('api/trim-video/', views.handle_video_trim, name='trim_video'),
    path('api/video-info/<str:video_id>/', views.get_video_info, name='video_info'),
]
