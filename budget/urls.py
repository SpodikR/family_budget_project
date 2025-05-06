# budget/urls.py
from django.urls import path
from . import views # Імпортуємо views з поточного каталогу (додатку)

app_name = 'budget' # Задаємо простір імен для URL-адрес цього додатку

urlpatterns = [
    # Головна сторінка (Дашборд)
    path('', views.dashboard, name='dashboard'),
    # Витрати
    # --- ОСНОВНИЙ URL ДЛЯ ДОДАВАННЯ ВИТРАТ (через формсет) ---
    path('expense/add/', views.add_expense, name='add_expense'), # <--- Перевір, що веде на твою view з формсетом
    # --- КІНЕЦЬ ОСНОВНОГО URL ---
    path('expense/<int:pk>/edit/', views.edit_expense, name='edit_expense'), # Для редагування однієї
    path('expense/<int:pk>/delete/', views.delete_expense, name='delete_expense'), # Для видалення однієї

    # Сторінка статистики для поточного місяця (без параметрів в URL)
    path('statistics/', views.monthly_statistics, name='monthly_statistics_current'),
    path('statistics/<int:year>/<int:month>/', views.monthly_statistics, name='monthly_statistics'),
    # Потік грошей
    path('cashflow/', views.cash_flow_view, name='cash_flow'),
    # Доходи
    path('income/add/', views.add_income, name='add_income'),
    path('income/<int:pk>/edit/', views.edit_income, name='edit_income'),
    path('income/<int:pk>/delete/', views.delete_income, name='delete_income'),
]