# budget/views.py
from django.shortcuts import render, redirect # render - для відображення шаблонів, redirect - для перенаправлення
from django.http import HttpResponse # Базовий HTTP-відповідь (для тестів)
from .models import Income, Expense, Category
from .forms import IncomeForm, ExpenseForm, CommonExpenseDataForm, ExpenseLineFormSet
from django.utils import timezone
from django.db.models import Sum, F # Для агрегації (підсумовування),F для роботи з полями
from datetime import datetime # Для роботи з датами
# --- ДОДАНО ---
# Декоратор для перевірки, чи користувач залогінений (опціонально, але корисно)
from django.contrib.auth.decorators import login_required
# Для отримання моделі User (хоча вона вже є в request.user)
from django.contrib.auth.models import User
# --- КІНЕЦЬ ДОДАНОГО ---
from django.db.models import Value, CharField, DecimalField # Для анотацій
from django.db.models.functions import Cast # Для перетворення типів
from decimal import Decimal # Для роботи з грошима
from .models import Category # Імпортуємо Category
import json # Для передачі даних в шаблон безпечно
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied # Для перевірки прав
from django.contrib import messages # Для повідомлень користувачу
from django.db import transaction # Для транзакцій (якщо потрібно)

# Головна сторінка / Дашборд
def dashboard(request):
    # Визначаємо, чиї дані показувати
    target_user = None
    if request.user.is_authenticated:
        target_user = request.user # Залогінений користувач
    # else: target_user залишається None (для гостя)
    # Отримуємо останні 5 доходів та витрат
    # Фільтруємо за target_user (або None для гостя)
    recent_incomes = Income.objects.filter(user=target_user).order_by('-date')[:5]
    recent_expenses = Expense.objects.filter(user=target_user).order_by('-date')[:5]

    # Базовий контекст для передачі в шаблон
    context = {
        'recent_incomes': recent_incomes,
        'recent_expenses': recent_expenses,
        # Передаємо користувача в шаблон, щоб знати, чиї дані відображаються
        'data_owner': target_user,
        'is_guest': not request.user.is_authenticated, # Прапорець, що це гість
    }
    # Рендеримо шаблон dashboard.html, передаючи йому контекст
    return render(request, 'budget/dashboard.html', context)

# View для додавання доходу (може робити і гість)
# View для додавання доходу (може робити і гість)
def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            # Створюємо об'єкт, але ще не зберігаємо в БД
            income_entry = form.save(commit=False)
            # Перевіряємо, чи користувач залогінений
            if request.user.is_authenticated:
                income_entry.user = request.user # Прив'язуємо до користувача
            # else: income_entry.user залишається None (для гостя)
            income_entry.save() # Тепер зберігаємо в БД
            return redirect('budget:dashboard')
    else:
        form = IncomeForm()

    context = {
        'form': form,
        'is_guest': not request.user.is_authenticated,
    }
    return render(request, 'budget/income_form.html', context)

# --- УНІВЕРСАЛЬНА VIEW ДЛЯ ДОДАВАННЯ ВИТРАТ ЧЕРЕЗ ФОРМСЕТ ---
@login_required
def add_expense(request): # Використовуємо цю назву для URL /expense/add/
    """Додавання однієї або кількох витрат за одну дату та категорію."""
    template_name = 'budget/expense_add_form.html' # Наш новий шаблон

    # Ініціалізуємо форми для GET запиту або при помилці POST
    # queryset=Expense.objects.none() - важливо для створення НОВИХ об'єктів
    formset = ExpenseLineFormSet(request.POST or None, request.FILES or None, queryset=Expense.objects.none(), prefix='expenses')
    common_data_form = CommonExpenseDataForm(request.POST or None)

    if request.method == 'POST':
        print("Обробка POST запиту...") # Лог
        # Перевіряємо валідність обох: форми спільних даних та формсету
        if common_data_form.is_valid() and formset.is_valid():
            print("Обидві форми валідні.") # Лог
            common_date = common_data_form.cleaned_data['date']
            common_category = common_data_form.cleaned_data['category']
            print(f"Спільна дата: {common_date}, Спільна категорія: {common_category.name}") # Лог

            # Використовуємо транзакцію, щоб гарантувати цілісність даних
            try:
                with transaction.atomic():
                    saved_count = 0
                    # Ітеруємо по формах у формсеті
                    for form in formset:
                        # cleaned_data існує тільки якщо форма валідна
                        # Перевіряємо, чи є сума - індикатор того, що рядок заповнено
                        if form.cleaned_data.get('amount'):
                            print(f"Обробка заповненої форми: {form.cleaned_data}") # Лог
                            # Створюємо об'єкт, але не зберігаємо одразу
                            expense = form.save(commit=False)
                            # Призначаємо спільні дані та користувача
                            expense.user = request.user
                            expense.date = common_date
                            expense.category = common_category
                            # Зберігаємо одну витрату
                            expense.save()
                            saved_count += 1
                        # Порожні форми ігноруються автоматично завдяки is_valid() та перевірці amount

                    if saved_count > 0:
                        messages.success(request, f"Успішно додано {saved_count} витрат(у) в категорію '{common_category.name}' за {common_date.strftime('%d.%m.%Y')}.")
                        print(f"Успішно збережено {saved_count} витрат.") # Лог
                    else:
                        messages.warning(request, "Не було додано жодної витрати (можливо, рядки були порожні або невалідні?).")
                        print("Не знайдено валідних рядків для збереження.") # Лог

                    # Перенаправляємо після успішного збереження
                    return redirect('budget:dashboard') # Або 'budget:add_expense' для повторного додавання

            except Exception as e:
                # Обробка можливих помилок під час збереження
                 print(f"Помилка під час транзакції збереження: {e}") # Лог
                 messages.error(request, f"Виникла помилка під час збереження даних: {e}")

        else: # Якщо одна з форм або формсет не валідні
            print("Форма спільних даних валідна:", common_data_form.is_valid()) # Лог
            print("Помилки форми спільних даних:", common_data_form.errors) # Лог
            print("Формсет валідний:", formset.is_valid()) # Лог
            # Виведемо помилки формсету більш детально
            if not formset.is_valid():
                 print("Загальні помилки формсету:", formset.non_form_errors())
                 for i, form_errors in enumerate(formset.errors):
                     if form_errors:
                         print(f"Помилки у формі #{i}:", form_errors)
            messages.error(request, "Будь ласка, виправте помилки, відмічені у формі.")

    # Для GET запиту або якщо POST був невалідним, рендеримо шаблон з формами
    context = {
        'formset': formset,
        'common_data_form': common_data_form,
    }
    print("Рендеринг шаблону...") # Лог
    return render(request, template_name, context)

# --- КІНЕЦЬ УНІВЕРСАЛЬНОЇ VIEW ---

# --- VIEW ДЛЯ РЕДАГУВАННЯ ВИТРАТИ ---
@login_required
def edit_expense(request, pk):
    """Редагування існуючої витрати."""
    expense = get_object_or_404(Expense, pk=pk) # Отримуємо витрату або 404
    template_name = 'budget/expense_form.html' # Назва шаблону

    # Перевірка прав доступу: чи є поточний користувач власником запису
    if expense.user != request.user:
        raise PermissionDenied("Ви не маєте права редагувати цю витрату.")

    if request.method == 'POST':
        # Ініціалізуємо форму POST-даними та файлами, прив'язуючи до існуючого об'єкту
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            form.save() # Зберігаємо зміни
            messages.success(request, f"Витрату '{expense}' успішно оновлено.")
            # Перенаправляємо на сторінку потоку грошей (або куди зручніше)
            return redirect('budget:cash_flow')
        else:
            # Якщо форма не валідна, показуємо помилки
             messages.error(request, "Будь ласка, виправте помилки у формі.")
    else: # GET-запит
        # Ініціалізуємо форму даними з існуючого об'єкту
        form = ExpenseForm(instance=expense)

    context = {
        'form': form,
        'is_editing': True, # Прапорець, що це режим редагування
        'object': expense # Передаємо сам об'єкт для можливого використання в шаблоні (напр. для заголовку)
    }
    # Використовуємо той самий шаблон, що і для додавання, але передаємо прапорець
    return render(request, template_name, context)


# --- VIEW ДЛЯ РЕДАГУВАННЯ ДОХОДУ ---
@login_required
def edit_income(request, pk):
    """Редагування існуючого доходу."""
    income = get_object_or_404(Income, pk=pk) # Отримуємо дохід або 404
    template_name = 'budget/income_form.html' # Назва шаблону

    # Перевірка прав доступу
    if income.user != request.user:
        raise PermissionDenied("Ви не маєте права редагувати цей дохід.")

    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income) # FILES тут не потрібні
        if form.is_valid():
            form.save()
            messages.success(request, f"Дохід '{income}' успішно оновлено.")
            return redirect('budget:cash_flow')
        else:
             messages.error(request, "Будь ласка, виправте помилки у формі.")
    else: # GET-запит
        form = IncomeForm(instance=income)

    context = {
        'form': form,
        'is_editing': True,
        'object': income
    }
    return render(request, template_name, context)

# --- VIEW ДЛЯ ВИДАЛЕННЯ ВИТРАТИ ---
@login_required
def delete_expense(request, pk):
    """Видалення існуючої витрати."""
    expense = get_object_or_404(Expense, pk=pk)
    template_name = 'budget/expense_confirm_delete.html' # Шаблон підтвердження

    # Перевірка прав доступу
    if expense.user != request.user:
        raise PermissionDenied("Ви не маєте права видаляти цю витрату.")

    if request.method == 'POST':
        # Якщо користувач підтвердив видалення (натиснув кнопку у формі)
        expense_repr = str(expense) # Зберігаємо текстове представлення для повідомлення
        expense.delete() # Видаляємо об'єкт з бази даних
        messages.success(request, f"Витрату '{expense_repr}' успішно видалено.")
        # Перенаправляємо на сторінку потоку грошей (або дашборд)
        return redirect('budget:cash_flow')
    else: # GET-запит
        # Просто показуємо сторінку підтвердження
        context = {'object': expense}
        return render(request, template_name, context)

# --- VIEW ДЛЯ ВИДАЛЕННЯ ДОХОДУ ---
@login_required
def delete_income(request, pk):
    """Видалення існуючого доходу."""
    income = get_object_or_404(Income, pk=pk)
    template_name = 'budget/income_confirm_delete.html' # Шаблон підтвердження

    # Перевірка прав доступу
    if income.user != request.user:
        raise PermissionDenied("Ви не маєте права видаляти цей дохід.")

    if request.method == 'POST':
        income_repr = str(income)
        income.delete()
        messages.success(request, f"Дохід '{income_repr}' успішно видалено.")
        return redirect('budget:cash_flow')
    else: # GET-запит
        context = {'object': income}
        return render(request, template_name, context)


# View для перегляду статистики за місяць
@login_required
def monthly_statistics(request, year=None, month=None):
    """
    Відображає статистику доходів та витрат за вказаний (або поточний) місяць,
    включаючи діаграму розподілу витрат за категоріями з кольорами.
    """
    print(f"--- monthly_statistics ---")
    print(f"Отримано з URL: year={repr(year)}, month={repr(month)}")

    target_user = request.user # Використовуємо залогіненого користувача
    current_year = timezone.now().year
    current_month = timezone.now().month

    # Ініціалізуємо значення за замовчуванням поточним роком/місяцем
    selected_year = current_year
    selected_month = current_month
    print(f"Значення за замовчуванням: рік={selected_year}, місяць={selected_month}")

    # 1. ВИЗНАЧАЄМО РІК ТА МІСЯЦЬ ДЛЯ ВИКОРИСТАННЯ
    try:
        # Якщо параметри передані з URL, намагаємося їх використати
        if year is not None and month is not None:
            parsed_year = int(year)
            parsed_month = int(month)
            # Перевіряємо коректність місяця
            if not (1 <= parsed_month <= 12):
                 print(f"!!! Некоректний місяць з URL: {month}. Використовую поточний.")
                 raise ValueError("Invalid month") # Спричинить перехід у except
            # Якщо все коректно, оновлюємо значення
            selected_year = parsed_year
            selected_month = parsed_month
            print(f"Параметри з URL успішно розпізнані: рік={selected_year}, місяць={selected_month}")
        # else: залишаться значення за замовчуванням (поточні), нічого не робимо

    except (ValueError, TypeError):
        # Якщо сталася помилка конвертації або тип неправильний,
        # selected_year/month залишаться зі значеннями за замовчуванням (current_year/month)
        print(f"!!! Помилка конвертації року/місяця з URL ({year}, {month}). Використовую поточні.")

    print(f"--- Будуть використані для фільтрації: рік={selected_year}, місяць={selected_month} ---")

    # 2. ФІЛЬТРУЄМО ДАНІ ЗА ВИЗНАЧЕНИМ ПЕРІОДОМ
    incomes = Income.objects.filter(user=target_user, date__year=selected_year, date__month=selected_month)
    expenses = Expense.objects.filter(user=target_user, date__year=selected_year, date__month=selected_month)
    print(f"Знайдено доходів: {incomes.count()}, витрат: {expenses.count()}")

    # 3. РОЗРАХУНКИ СУМ ТА БАЛАНСУ
    total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    balance = total_income - total_expense

    # 4. ДАНІ ДЛЯ ДІАГРАМИ (використовуємо вже відфільтровані expenses)
    category_summary = expenses.filter(category__isnull=False) \
                                .values('category__name', 'category__color') \
                                .annotate(total=Sum('amount')) \
                                .order_by('-total')
    chart_labels = []
    chart_data = []
    chart_colors = []
    default_color = '#CCCCCC'
    color_palette = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40',
        '#E7E9ED', '#83FF63', '#63C6FF', '#FF8A56', '#C04BBC', '#66FF99'
    ]
    color_index = 0

    for item in category_summary:
        chart_labels.append(item['category__name'])
        chart_data.append(float(item['total']))
        color = item['category__color']
        # Використовуємо колір з палітри, якщо в категорії немає кольору або він сірий за замовчуванням
        if not color or color == '#808080' or color == '#CCCCCC': # Додав перевірку і на другий сірий
             color = color_palette[color_index % len(color_palette)]
             color_index += 1
        chart_colors.append(color)
    has_expense_data = bool(chart_data)

    # 5. ГЕНЕРАЦІЯ СПИСКУ МІСЯЦІВ ДЛЯ SELECT
    # Отримуємо всі місяці, де були хоч якісь записи у користувача
    income_dates_qs = Income.objects.filter(user=target_user).dates('date', 'month', order='DESC')
    expense_dates_qs = Expense.objects.filter(user=target_user).dates('date', 'month', order='DESC')
    # Отримуємо унікальні пари (рік, місяць)
    unique_months = set((d.year, d.month) for d in income_dates_qs) | set((d.year, d.month) for d in expense_dates_qs)
    # Сортуємо (спочатку найновіші)
    sorted_months = sorted(list(unique_months), reverse=True)
    month_list = []
    for y_opt, m_opt in sorted_months:
        try:
            month_name_for_list = datetime(y_opt, m_opt, 1).strftime('%B %Y').title()
            month_list.append({'year': y_opt, 'month': m_opt, 'name': month_name_for_list})
        except ValueError: continue

    # 6. ФОРМУВАННЯ НАЗВИ МІСЯЦЯ ДЛЯ ЗАГОЛОВКУ
    try:
        month_name = datetime(selected_year, selected_month, 1).strftime('%B %Y').title()
    except ValueError:
        month_name = f"Некоректний місяць ({selected_year}-{selected_month})"

    # 7. ФОРМУВАННЯ КОНТЕКСТУ ДЛЯ ШАБЛОНУ
    context = {
        'year': selected_year,
        'month': selected_month,
        'month_name': month_name,
        'incomes': incomes,
        'expenses': expenses, # Передаємо всі витрати (включаючи ті, що без категорії) для списку
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'month_list': month_list,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'chart_colors': json.dumps(chart_colors),
        'has_expense_data': has_expense_data,
    }

    print(f"--- Передаю в шаблон: рік={context['year']}, місяць={context['month']} ---")
    return render(request, 'budget/monthly_statistics.html', context)
@login_required
def cash_flow_view(request):
    """
    Відображає хронологічний список усіх доходів та витрат
    з розрахунком біжучого балансу.
    """
    # Отримуємо всі доходи та витрати поточного користувача
    incomes = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)

    # Створюємо список словників для уніфікованого представлення
    transactions_list = []

    for income in incomes:
        transactions_list.append({
            'date': income.date,
            'type': 'income', # Тип операції
            'description': income.source or f"Дохід #{income.pk}", # Опис (джерело або ID)
            'category': None, # Доходи не мають категорії в нашій моделі
            'amount': income.amount, # Сума (завжди позитивна для доходу)
            'pk': income.pk, # ID для можливих посилань на редагування/видалення
        })

    for expense in expenses:
        transactions_list.append({
            'receipt_image_url': expense.receipt_image.url if expense.receipt_image else None,
            'date': expense.date,
            'type': 'expense', # Тип операції
            'description': expense.description or f"Витрата #{expense.pk}", # Опис
            'category': expense.category.name if expense.category else "Без категорії", # Назва категорії
            # Зберігаємо витрату як НЕГАТИВНЕ число для легшого розрахунку балансу
            'amount': -expense.amount,
            'pk': expense.pk, # ID
        })

    # Сортуємо об'єднаний список строго за датою
    # Якщо дати однакові, можна додати сортування за pk або іншим полем для стабільності
    transactions_list.sort(key=lambda x: (x['date'], x['pk'] if x['type'] == 'income' else -x['pk'])) # Сортуємо за датою, потім доходи перед витратами (?)

    # Розраховуємо біжучий баланс
    running_balance = Decimal('0.00') # Починаємо з нуля
    for transaction in transactions_list:
        running_balance += transaction['amount'] # Додаємо суму (позитивну для доходу, негативну для витрати)
        transaction['balance_after'] = running_balance # Зберігаємо баланс ПІСЛЯ цієї операції
         # --- ДОДАНО ---
        # Зберігаємо позитивне значення для відображення
        transaction['display_amount'] = abs(transaction['amount'])
        # --- КІНЕЦЬ ДОДАНОГО ---

    context = {
        'transactions': transactions_list,
    }
    return render(request, 'budget/cash_flow.html', context)

# --- КІНЕЦЬ НОВОЇ VIEW ---