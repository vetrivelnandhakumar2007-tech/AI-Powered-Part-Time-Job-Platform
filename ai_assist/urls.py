from django.urls import path

from . import views

app_name = 'ai_assist'

urlpatterns = [
    path('chat/', views.chat_view, name='chat'),
]
