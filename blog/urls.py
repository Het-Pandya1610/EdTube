from django.urls import path
from . import views

urlpatterns = [
    path("", views.blog, name="blog"),
    path("blog1-details/",views.blog1, name="blog1"),
    path("blog2-details/",views.blog2, name="blog2"),
    path("blog3-details/",views.blog3, name="blog3"),
    path("blog4-details/",views.blog4, name="blog4"),
]