from django.urls import path
from .views import (
    NoteListView,
    NoteDetailView,
    NoteCreateView,
    NoteUpdateView,
    NoteDeleteView,
    # --- ДОДАНО ---
    export_notes_json,
    import_notes_json,
    # --- КІНЕЦЬ ДОДАНОГО ---
)

app_name = 'notes'

urlpatterns = [
    path('', NoteListView.as_view(), name='note_list'),                     # Список нотаток
    path('new/', NoteCreateView.as_view(), name='note_create'),             # Створення нової нотатки
    path('<int:pk>/', NoteDetailView.as_view(), name='note_detail'),        # Перегляд деталей
    path('<int:pk>/edit/', NoteUpdateView.as_view(), name='note_update'),   # Редагування
    path('<int:pk>/delete/', NoteDeleteView.as_view(), name='note_delete'), # Видалення
    # --- НОВІ URL ---
    path('export/', export_notes_json, name='export_notes'),
    path('import/', import_notes_json, name='import_notes'),
    # --- КІНЕЦЬ НОВИХ URL ---
]