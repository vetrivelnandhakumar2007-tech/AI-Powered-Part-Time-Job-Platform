from django.urls import path

from . import views

app_name = 'reviews'

urlpatterns = [
    path('job/<int:job_pk>/review/<int:to_user_pk>/', views.leave_review, name='leave_review'),
]
