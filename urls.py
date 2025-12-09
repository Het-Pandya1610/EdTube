"""
URL configuration for EduNex project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('Home', views.index, name="index"),
    path('register', views.reg, name="reg"),
    path('faqs', views.faqs, name="faqs"),
    path('terms', views.terms, name="terms"),
    path('help-center', views.helpCenter, name="help"),
    path('courses', views.courses, name="courses"),
    path('contact', views.contact, name="contact"),
    path('privacy-policy', views.privacyPolicy, name="policy"),
    path('blog', views.blog, name="blog"),
    path('blog-details', views.blog1, name="blog1"),
    path('blog2-details', views.blog2, name="blog2"),
    path('blog3-details', views.blog3, name="blog3"),
    path('blog4-details', views.blog4, name="blog4"),
    path('report-issue', views.reportIssue, name="reportIssue"),
    path('reviews', views.reviews, name="reviews"),
    path('about-us', views.aboutUs, name="AboutUs"),
    path('login', views.login_view, name="login"),
]
