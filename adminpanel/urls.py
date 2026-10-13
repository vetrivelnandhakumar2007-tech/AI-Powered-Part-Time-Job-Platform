from django.urls import path

from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),

    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:pk>/edit/', views.job_edit, name='job_edit'),
    path('jobs/<int:pk>/delete/', views.job_delete, name='job_delete'),

    path('applications/', views.application_list, name='application_list'),
    path('applications/<int:pk>/edit/', views.application_edit, name='application_edit'),
    path('applications/<int:pk>/delete/', views.application_delete, name='application_delete'),

    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    path('reviews/', views.review_list, name='review_list'),
    path('reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),

    path('site-settings/', views.site_settings_edit, name='site_settings_edit'),

    path('hero-slides/', views.hero_slide_list, name='hero_slide_list'),
    path('hero-slides/create/', views.hero_slide_create, name='hero_slide_create'),
    path('hero-slides/<int:pk>/edit/', views.hero_slide_edit, name='hero_slide_edit'),
    path('hero-slides/<int:pk>/delete/', views.hero_slide_delete, name='hero_slide_delete'),

    path('about-features/', views.about_feature_list, name='about_feature_list'),
    path('about-features/create/', views.about_feature_create, name='about_feature_create'),
    path('about-features/<int:pk>/edit/', views.about_feature_edit, name='about_feature_edit'),
    path('about-features/<int:pk>/delete/', views.about_feature_delete, name='about_feature_delete'),
]
