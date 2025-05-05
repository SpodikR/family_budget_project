from django.db import models
from django.utils import timezone # Для роботи з датами та часом
# --- ДОДАНО ---
# Імпортуємо модель User зі стандартного пакету аутентифікації Django
from django.contrib.auth.models import User
# --- КІНЕЦЬ ДОДАНОГО ---
from django.conf import settings # Для MEDIA_URL

# Модель для категорій витрат (Продукти, Транспорт, Навчання тощо)
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Назва категорії")  # Назва категорії
    # --- ДОДАНО ПОЛЕ ---
    # Зберігаємо колір у форматі HEX. null=True, blank=True - для існуючих категорій
    # та якщо колір не обов'язковий. default - колір за замовчуванням.
    color = models.CharField(
        max_length=7, # Довжина HEX-коду (#RRGGBB)
        default='#808080', # Сірий колір за замовчуванням
        help_text="Введіть HEX-код кольору (наприклад, #FF5733)",
        verbose_name="Колір для діаграм"
        # Можна додати валідатор для перевірки формату HEX
    )
    # --- КІНЕЦЬ ДОДАНОГО ПОЛЯ ---

    # Як об'єкт буде відображатися в адмінці та при виводі
    def __str__(self):
        return self.name
    
    # Додаткові налаштування моделі для адмін-панелі
    class Meta:
        verbose_name = "Категорія" # Назва моделі в однині
        verbose_name_plural = "Категорії" # Назва моделі в множині

# Модель для записів про доходи
class Income(models.Model):
     # --- ДОДАНО ---
    # Зв'язок з користувачем, який створив цей запис.
    # on_delete=models.CASCADE: Якщо користувача видалять, всі його записи доходів теж видаляться.
    # null=True, blank=True: Дозволяє створювати записи без прив'язки до користувача (для гостей).
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Користувач")
    # --- КІНЕЦЬ ДОДАНОГО ---
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сума") # DecimalField краще для грошей
    date = models.DateField(default=timezone.now, verbose_name="Дата отримання") # Дата, за замовчуванням - сьогодні
    source = models.CharField(max_length=100, blank=True, null=True, verbose_name="Джерело доходу") # # Наприклад, 'Зарплата', 'Аванс', 'Премія'
    description = models.TextField(blank=True, null=True, verbose_name="Опис") # Додатковий опис

    # Як об'єкт буде відображатися в адмінці та при виводі
    def __str__(self):
        return f"{self.date} - {self.amount} грн ({self.source or "Дохід"})" # Виводимо дату, суму та джерело доходу
    
    class Meta:
        verbose_name = "Дохід"
        verbose_name_plural = "Доходи"
        ordering = ['-date']  # Сортування за датою (новіші спочатку)

# Модель для записів про витрати
class Expense(models.Model):
     # --- ДОДАНО ---
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Користувач")
    # --- КІНЕЦЬ ДОДАНОГО ---
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сума") # Сума витрат
    date = models.DateField(default=timezone.now, verbose_name="Дата витрат") # Дата витрат
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Категорія") # Зв'язок з моделлю Category. SET_NULL - якщо категорію видалять, поле стане порожнім
    description = models.TextField(blank=True, null=True, verbose_name="Опис") # Додатковий опис
    # --- НОВЕ ПОЛЕ ---
    # ImageField для збереження фото чеку.
    # upload_to='receipts/%Y/%m/%d/' - шлях куди зберігати файли відносно MEDIA_ROOT.
    # Django автоматично створить папки за роком/місяцем/днем.
    # blank=True, null=True - робить поле необов'язковим.
    receipt_image = models.ImageField(
        upload_to='receipts/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Фото або скрін чеку"
    )
    # --- КІНЕЦЬ НОВОГО ПОЛЯ ---

    # Як об'єкт буде відображатися в адмінці та при виводі
    def __str__(self):
        category_name = self.category.name if self.category else "Без категорії"  # Якщо категорія не вказана, виводимо "Без категорії"
        return f"{self.date} - {self.amount} грн ({category_name})" # Виводимо дату, суму та категорію
    
    class Meta:
        verbose_name = "Витрата"
        verbose_name_plural = "Витрати"
        ordering = ['-date']  # Сортування за датою (новіші спочатку)

