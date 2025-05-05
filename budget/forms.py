# budget/forms.py
from django import forms
from .models import Income, Expense, Category # Імпортуємо моделі Income, Expense та Category

# Форма для додавання/редагування доходу
class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income # На якій моделі базується форма
        # Виключаємо 'user' з полів форми
        fields = ['amount', 'date', 'source', 'description'] # Які поля включити у форму
        # Додаємо віджети для кращого вигляду, особливо для дати
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), # HTML5 date picker
            'amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}), # Дозволяє вводити копійки
            'source': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        # Можна перевизначити мітки полів (labels), якщо потрібно
        labels = {
            'amount': 'Сума доходу',
            'date': 'Дата',
            'source': 'Джерело',
            'description': 'Опис (необов\'язково)',
        }

# Форма для додавання/редагування витрати
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        # Виключаємо 'user' з полів форми
        fields = ['amount', 'date', 'category', 'description', 'receipt_image'] # Додали receipt_image
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}), # Випадаючий список для категорій
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            # Можна додати віджет і для файлу, щоб застосувати стилі Bootstrap
            'receipt_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'amount': 'Сума витрати',
            'date': 'Дата',
            'category': 'Категорія',
            'description': 'Опис (необов\'язково)',
            'receipt_image': 'Фото чеку (необов\'язково)', # Оновлюємо мітку
        }

class CategoryAdminForm(forms.ModelForm):
    # Використовуємо HTML5 Color Input віджет
    color = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'color'}),
        label="Колір для діаграм",
        help_text="Виберіть колір"
    )

    class Meta:
        model = Category
        fields = '__all__' # Включити всі поля моделі у форму адмінки