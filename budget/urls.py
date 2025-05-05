# budget/urls.py
from django.urls import path
from . import views # Імпортуємо views з поточного каталогу (додатку)

app_name = 'budget' # Задаємо простір імен для URL-адрес цього додатку

urlpatterns = [
    # Головна сторінка (Дашборд)
    path('', views.dashboard, name='dashboard'),

    # Сторінка для додавання доходу
    path('income/add/', views.add_income, name='add_income'),

    # Сторінка для додавання витрати
    path('expense/add/', views.add_expense, name='add_expense'),

    # Сторінка статистики для поточного місяця (без параметрів в URL)
    path('statistics/', views.monthly_statistics, name='monthly_statistics_current'),

    # Сторінка статистики для конкретного місяця (з параметрами рік/місяць)
    # Наприклад: /statistics/2024/3/
    path('statistics/<int:year>/<int:month>/', views.monthly_statistics, name='monthly_statistics'),
    # --- НОВИЙ URL ---
    path('cashflow/', views.cash_flow_view, name='cash_flow'),
    # --- КІНЕЦЬ НОВОГО URL ---
    path('income/<int:pk>/edit/', views.edit_income, name='edit_income'),
    path('income/<int:pk>/delete/', views.delete_income, name='delete_income'),
    path('expense/<int:pk>/edit/', views.edit_expense, name='edit_expense'),
    path('expense/<int:pk>/delete/', views.delete_expense, name='delete_expense'),
]