from django.urls import path
from . import views

urlpatterns = [
    path("upload",views.videoUpload,name="videoUpload"),
    path('watch/', views.watchVideo, name='watch_video'),
    path('history/', views.videoHistory, name="vidhistory"),
]
