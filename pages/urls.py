from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('faqs/', views.faqs, name='faqs'),
    path('terms/', views.terms, name='terms'),
    path('reviews/', views.reviews, name='reviews'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('report-issue/', views.reportIssue, name='reportIssue'),
    path('privacy-policy/', views.privacyPolicy, name='policy'),
    path('help-center/', views.helpCenter, name='help'),
    path('contact/', views.contact, name='contact'),
    path('about-us/', views.aboutUs, name='AboutUs'),
    path('search/', views.search, name='search_alt'),
    path('search-results/',views.search,name='search'),
    path('api/search-suggestions/', views.get_search_suggestions, name='search_suggestions_api'),
    path('api/delete-search-history/', views.delete_search_suggestion, name='delete_search_history'),
    path('api/upload-profile-image/', views.upload_profile_image, name='upload_profile_image'),
    path('@<str:username>/', views.user_profile, name='user_profile'),
]
