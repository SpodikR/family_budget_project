# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login # Для автоматичного входу після реєстрації
from .forms import RegistrationForm
# from django.contrib import messages # Для повідомлень

def register(request):
    if request.user.is_authenticated: # Якщо користувач вже залогінений, перенаправляємо
        return redirect('budget:dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save() # Зберігаємо нового користувача
            login(request, user) # Автоматично логінимо користувача
            # messages.success(request, 'Реєстрація успішна! Ви увійшли в систему.')
            return redirect('budget:dashboard') # Перенаправляємо на дашборд
        # else: форма з помилками буде показана знову
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})
