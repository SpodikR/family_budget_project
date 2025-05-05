# notes/admin.py
from django.contrib import admin
from .models import Note, NotePhoto

# Inline модель для фотографій
class NotePhotoInline(admin.TabularInline): # або admin.StackedInline для іншого вигляду
    model = NotePhoto
    extra = 1  # Кількість порожніх форм для додавання нових фото
    fields = ('image', 'caption') # Які поля показувати в inline формі
    readonly_fields = ('uploaded_at',) # Показувати, але не редагувати

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date', 'created_at')
    list_filter = ('user', 'date')
    search_fields = ('title', 'content', 'user__username')
    inlines = [NotePhotoInline] # Додаємо inline керування фотографіями
    readonly_fields = ('created_at', 'updated_at') # Ці поля встановлюються автоматично

@admin.register(NotePhoto)
class NotePhotoAdmin(admin.ModelAdmin):
    list_display = ('note', 'caption', 'uploaded_at')
    list_filter = ('note__user', 'note__date') # Фільтр за користувачем/датою нотатки
    search_fields = ('caption', 'note__title')
    list_select_related = ('note', 'note__user') # Оптимізація запитів
    readonly_fields = ('uploaded_at',)
