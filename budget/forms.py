# budget/forms.py
from django import forms
from django.forms import modelformset_factory # <--- Додаємо імпорт
from .models import Income, Expense, Category
from django.utils import timezone

# --- ФОРМА ДОХОДІВ (залишається як є) ---
class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['amount', 'date', 'source', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'source': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'amount': 'Сума доходу',
            'date': 'Дата',
            'source': 'Джерело',
            'description': 'Опис (необов\'язково)',
        }

# --- ФОРМА ДЛЯ РЕДАГУВАННЯ/ДОДАВАННЯ ОДНІЄЇ ВИТРАТИ (залишається) ---
# Вона буде використовуватися на сторінці редагування /expense/<pk>/edit/
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'date', 'category', 'description', 'receipt_image']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'receipt_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'amount': 'Сума витрати',
            'date': 'Дата',
            'category': 'Категорія',
            'description': 'Опис (необов\'язково)',
            'receipt_image': 'Фото чеку (необов\'язково)',
        }

# --- НОВА ФОРМА ДЛЯ ОДНОГО РЯДКА ВИТРАТИ У ФОРМСЕТІ ---
class ExpenseLineForm(forms.ModelForm):
    class Meta:
        model = Expense
        # Включаємо тільки поля, що стосуються конкретної витрати в рядку
        fields = ['amount', 'description', 'receipt_image']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control', 'placeholder': 'Сума'}), # Додав плейсхолдер
            'description': forms.Textarea(attrs={'rows': 1, 'class': 'form-control', 'placeholder': 'Опис (необов\'язково)'}), # Зменшив rows, додав плейсхолдер
            'receipt_image': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm'}), # Зробив поле файлу меншим
        }
        # labels тут не обов'язкові, якщо вони будуть у заголовках таблиці/рядків
        # labels = { 'amount': 'Сума', 'description': 'Опис', 'receipt_image': 'Чек', }

# --- НОВИЙ ФОРМСЕТ ДЛЯ РЯДКІВ ВИТРАТ ---
ExpenseLineFormSet = modelformset_factory(
    Expense,
    form=ExpenseLineForm, # Використовуємо форму рядка
    exclude=('user', 'date', 'category'), # Виключаємо спільні поля
    extra=5,  # Кількість порожніх форм за замовчуванням (зміни за потреби)
    can_delete=False
)

# --- НОВА ФОРМА ДЛЯ СПІЛЬНИХ ДАНИХ (ДАТА + КАТЕГОРІЯ) ---
class CommonExpenseDataForm(forms.Form):
    date = forms.DateField(
        label="Спільна дата*", # Додав * для позначення обов'язковості
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True,
        initial=timezone.now # <--- ДОДАНО ЦЕЙ ПАРАМЕТР
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all().order_by('name'),
        label="Спільна категорія*", # Додав *
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        empty_label=None # Не дозволяти порожній вибір
    )

# --- ФОРМА ДЛЯ АДМІНКИ КАТЕГОРІЙ (залишається як є) ---
class CategoryAdminForm(forms.ModelForm):
    color = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'color'}),
        label="Колір для діаграм",
        help_text="Виберіть колір"
    )
    class Meta:
        model = Category
        fields = '__all__'