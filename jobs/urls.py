from django.urls import path

from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('mine/', views.my_jobs, name='my_jobs'),
    path('create/', views.job_create, name='job_create'),
    path('<int:pk>/', views.job_detail, name='job_detail'),
    path('<int:pk>/edit/', views.job_edit, name='job_edit'),
    path('<int:pk>/close/', views.job_close, name='job_close'),
]
