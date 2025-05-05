import locale # Додай на початку файлу
from django.contrib import admin
from django.db import models
from .models import Expense, Income, Category # Імпортуємо наші моделі
from .forms import CategoryAdminForm # Імпортуємо форму для адмінки
from django.db.models.functions import Lower # Імпортуємо функцію для регістрованого сортування

# Налаштування відображення моделі Category в адмінці
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm # <--- Вказуємо використовувати нашу форму
    list_display = ('name',)  # Поля, які відображаються в списку
    search_fields = ('name',)  # Поле для пошуку
    # --- ДОДАЄМО ЦЕЙ МЕТОД ---
    def get_queryset(self, request):
        # Отримуємо базовий queryset
        qs = super().get_queryset(request)

        # Налаштовуємо локаль для правильного сортування українською
        # Спробуй один з цих варіантів локалі (залежить від твоєї ОС)
        # Можливо, потрібно буде встановити відповідну локаль в системі
        try:
            # Для Linux/macOS часто 'uk_UA.UTF-8'
            locale.setlocale(locale.LC_COLLATE, 'uk_UA.UTF-8')
        except locale.Error:
            try:
                # Для Windows часто 'ukr_ukr' або 'Ukrainian_Ukraine.1251'
                locale.setlocale(locale.LC_COLLATE, 'ukr_ukr')
            except locale.Error:
                print("Warning: Не вдалося встановити українську локаль для сортування в адмінці.")
                # Якщо не вдалося, сортування буде стандартним (можливо, неправильним)
                pass

        # Отримуємо всі об'єкти і сортуємо їх у Python за допомогою locale.strxfrm
        # locale.strxfrm перетворює рядок так, щоб стандартне сортування працювало коректно для поточної локалі
        # Перетворюємо queryset на список, щоб сортувати в пам'яті
        # УВАГА: Це може бути неефективно для ДУЖЕ великої кількості категорій
        sorted_list = sorted(list(qs), key=lambda category: locale.strxfrm(category.name))

        # Повертаємо queryset, відфільтрований за ID відсортованого списку
        # Це трохи складний трюк, щоб зберегти можливість пагінації в адмінці
        # Він зберігає порядок зі sorted_list
        pk_list = [category.pk for category in sorted_list]
        # Створюємо умову для збереження порядку
        preserved = models.Case(*[models.When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
        return qs.filter(pk__in=pk_list).order_by(preserved)
        # Альтернатива (простіша, але може зламати пагінацію):
        # return qs.filter(pk__in=pk_list) # Порядок може не зберегтися
        # Або повернути список (зламає багато функцій адмінки):
        # return sorted_list
    # --- КІНЕЦЬ МЕТОДУ ---

     # Додатковий метод для відображення кольору в списку
    def color_display(self, obj):
        from django.utils.html import format_html
        if obj.color:
            return format_html(
                '<div style="width: 30px; height: 20px; background-color: {0}; border: 1px solid #ccc;" title="{0}"></div>',
                obj.color
            )
        return "-"
    color_display.short_description = 'Колір' # Назва стовпця

# Налаштування відображення моделі Income в адмінці
@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    # Додаємо 'user' до list_display та list_filter
    list_display = ('user', 'date', 'amount', 'source', 'description')  # Поля, які відображаються в списку
    list_filter = ('user', 'date', 'source')  # Фільтри збоку, # Фільтр за користувачем
    search_fields = ('user__username', 'source', 'description')  # Поле для пошуку, # Пошук за іменем користувача
    date_hierarchy = 'date'  # Навігація за датою зверху
    # Оптимізація: Завантажувати пов'язаного користувача одразу
    list_select_related = ('user',)

# Налаштування відображення моделі Expense в адмінці
@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    # Додаємо 'receipt_image' до list_display
    # Додаємо 'user' до list_display та list_filter
    list_display = ('user', 'date', 'amount', 'category', 'receipt_image', 'description')
    list_filter = ('user', 'date', 'category') # Фільтр за користувачем
    search_fields = ('user__username', 'category__name', 'description')  # Пошук за назвою категорії, # Пошук за іменем користувача
    date_hierarchy = 'date'
    list_select_related = ('category',)  # Оптимізація: завантажувати пов'язану категорію одразу
    # Можна додати поле до readonly_fields, щоб бачити прев'ю в детальному вигляді
    # readonly_fields = ('receipt_image_preview',) # Потребує додавання методу в модель

    # Якщо хочете бачити саме зображення в адмінці (потребує дод. налаштувань)
    # def receipt_image_preview(self, obj):
    #     from django.utils.html import format_html
    #     if obj.receipt_image:
    #         return format_html('<a href="{0}"><img src="{0}" style="max-width: 100px; max-height: 100px;" /></a>', obj.receipt_image.url)
    #     return "(Немає зображення)"
    # receipt_image_preview.short_description = 'Прев\'ю чеку'

# --- АБО простіший варіант реєстрації (без додаткових налаштувань) ---
# admin.site.register(Category)
# admin.site.register(Income)
# admin.site.register(Expense)
# --------------------------------------------------------------------
