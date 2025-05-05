# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Обов\'язкове поле. Потрібне для відновлення паролю.')
    first_name = forms.CharField(required=False, label='Ім\'я') # Зробив необов'язковим для прикладу
    last_name = forms.CharField(required=False, label='Прізвище') # Зробив необов'язковим

    class Meta(UserCreationForm.Meta):
        model = User
        # Вказуємо поля, включаючи додані нами
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо клас 'form-control' до всіх видимих полів
        for field_name, field in self.fields.items():
            # Додаємо клас за замовчуванням
            field.widget.attrs.update({'class': 'form-control'})
            # Можна додати плейсхолдер, якщо хочете
            field.widget.attrs.update({'placeholder': field.label})

            # Обробка помилок (додавання is-invalid) краще робити в шаблоні,
            # бо тут ми не знаємо, чи є помилки на момент ініціалізації.