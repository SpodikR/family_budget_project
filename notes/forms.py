# notes/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Note, NotePhoto

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['date', 'title', 'content'] # 'user' встановлюється у view
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        }
        labels = {
            'date': 'Дата запису',
            'title': 'Заголовок/Тема',
            'content': 'Зміст нотатки',
        }

class NotePhotoForm(forms.ModelForm):
    """Форма для окремої фотографії (використовується в формсеті)"""
    class Meta:
        model = NotePhoto
        fields = ['image', 'caption']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Необов\'язковий підпис'}),
        }
        labels = {
            'image': 'Файл фото',
            'caption': 'Підпис',
        }

# Фабрика для створення інлайн-формсету для фотографій
NotePhotoFormSet = inlineformset_factory(
    Note,             # Батьківська модель
    NotePhoto,        # Дочірня модель (модель фото)
    form=NotePhotoForm, # Форма для кожного фото
    fields=['image', 'caption'], # Поля для формсету
    extra=1,          # Кількість порожніх форм для нових фото
    can_delete=True     # Дозволити видалення існуючих фото через чекбокс
)

class NoteImportForm(forms.Form):
    """Форма для завантаження JSON файлу для імпорту нотаток."""
    json_file = forms.FileField(
        label="Виберіть JSON файл",
        help_text="Файл має бути у форматі JSON та містити список нотаток.",
        widget=forms.ClearableFileInput(attrs={'accept': '.json', 'class': 'form-control'})
    )