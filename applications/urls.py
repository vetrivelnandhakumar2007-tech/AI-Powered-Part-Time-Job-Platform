from django.urls import path

from . import views

app_name = 'applications'

urlpatterns = [
    path('apply/<int:job_pk>/', views.apply_to_job, name='apply_to_job'),
    path('mine/', views.my_applications, name='my_applications'),
    path('job/<int:job_pk>/applicants/', views.job_applicants, name='job_applicants'),
    path('<int:pk>/status/<str:new_status>/', views.update_application_status, name='update_status'),
]
