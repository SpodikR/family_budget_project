# accounts/urls.py
from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    # Підключаємо стандартні URL для входу/виходу тощо
    # Тепер вони будуть доступні як /accounts/login/, /accounts/logout/
    path('', include('django.contrib.auth.urls')),
]