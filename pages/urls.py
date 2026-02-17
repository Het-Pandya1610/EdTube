from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('notifications/', views.notifications, name='notifications'),
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
    path('get-search-suggestions/', views.get_search_suggestions, name='get_search_suggestions'),
    path('delete-search-suggestion/', views.delete_search_suggestion, name='delete_search_suggestion'),
    path('clear-search-history/', views.clear_search_history, name='clear_search_history'),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),
    path('api/upload-profile-image/', views.upload_profile_image, name='upload_profile_image'),
    path('@<str:username>/', views.user_profile, name='user_profile'),
]
