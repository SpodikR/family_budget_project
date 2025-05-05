# family_budget/urls.py
from django.contrib import admin
from django.urls import path, include # Додайте include
# --- ДОДАНО ---
from django.conf import settings
from django.conf.urls.static import static
# --- КІНЕЦЬ ДОДАНОГО ---

urlpatterns = [
    path('admin/', admin.site.urls),
     # --- ДОДАНО ---
    # Підключаємо стандартні URL для автентифікації (login, logout, password reset, etc.)
    # Вони будуть доступні за адресами /accounts/login/, /accounts/logout/ і т.д.
    # Підключаємо URL з додатку accounts
    path('accounts/', include('accounts.urls')),
    # path('accounts/', include('django.contrib.auth.urls')),
    # --- КІНЕЦЬ ДОДАНОГО ---
    # Підключаємо всі URL-адреси з файлу budget/urls.py
    # Всі адреси з додатку budget будуть доступні без префіксу (на кореневому рівні сайту)
    path('', include('budget.urls')),
    # Якщо б ми написали path('budget/', include('budget.urls')), то адреси були б
    # /budget/, /budget/income/add/ і т.д.
    # --- ДОДАЄМО URLи ДОДАТКУ NOTES ---
    path('notes/', include('notes.urls')),
    # --- КІНЕЦЬ ДОДАНОГО ---
]

# --- ДОДАНО ---
# Цей код додає URL-патерн для роздачі медіа файлів
# ТІЛЬКИ в режимі DEBUG (під час розробки).
# На production сервері цим повинен займатися веб-сервер (Nginx/Apache).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# --- КІНЕЦЬ ДОДАНОГО ---
