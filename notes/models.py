# notes/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse # Для генерації URL об'єкта

class Note(models.Model):
    """Модель для нотатки/запису."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Користувач")
    date = models.DateField(default=timezone.now, verbose_name="Дата запису")
    title = models.CharField(max_length=200, verbose_name="Заголовок/Тема")
    content = models.TextField(verbose_name="Зміст нотатки")
    created_at = models.DateTimeField(auto_now_add=True) # Дата створення (автоматично)
    updated_at = models.DateTimeField(auto_now=True)     # Дата оновлення (автоматично)

    def __str__(self):
        return f"{self.date.strftime('%d.%m.%Y')} - {self.title} ({self.user.username})"

    def get_absolute_url(self):
        # Повертає URL для перегляду конкретної нотатки
        return reverse('notes:note_detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = "Нотатка"
        verbose_name_plural = "Нотатки"
        ordering = ['-date', '-created_at'] # Сортування: новіші дати спочатку

class NotePhoto(models.Model):
    """Модель для фотографії, пов'язаної з нотаткою."""
    note = models.ForeignKey(Note, related_name='photos', on_delete=models.CASCADE, verbose_name="Нотатка")
    image = models.ImageField(upload_to='notes_photos/%Y/%m/%d/', verbose_name="Фото")
    caption = models.CharField(max_length=255, blank=True, null=True, verbose_name="Підпис до фото")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Фото до нотатки '{self.note.title}' ({self.note.date.strftime('%d.%m.%Y')})"

    class Meta:
        verbose_name = "Фото до нотатки"
        verbose_name_plural = "Фото до нотаток"
        ordering = ['uploaded_at'] # Старіші фото спочатку для конкретної нотатки
