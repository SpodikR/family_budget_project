# notes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Note, NotePhoto
from .forms import NoteForm, NotePhotoFormSet, NoteImportForm # Додамо NoteImportForm
from django.db import transaction # Для атомарних операцій з формсетом
from django.contrib import messages
import json
from django.http import HttpResponse, JsonResponse # Додаємо HttpResponse, JsonResponse
from django.utils import timezone # Для обробки дат при імпорті
from django.core.exceptions import ValidationError

# --- Використаємо Class-Based Views для різноманітності та лаконічності ---

class NoteListView(LoginRequiredMixin, ListView):
    """Показує список нотаток поточного користувача."""
    model = Note
    template_name = 'notes/note_list.html'
    context_object_name = 'notes'
    paginate_by = 10 # Додамо пагінацію

    def get_queryset(self):
        # Показуємо тільки нотатки залогіненого користувача
        return Note.objects.filter(user=self.request.user).order_by('-date', '-created_at')

class NoteDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Показує деталі однієї нотатки та її фото."""
    model = Note
    template_name = 'notes/note_detail.html'
    context_object_name = 'note'

    def test_func(self):
        # Перевірка, що користувач є власником нотатки
        note = self.get_object()
        return self.request.user == note.user

class NoteCreateView(LoginRequiredMixin, CreateView):
    """Створення нової нотатки з фотографіями."""
    model = Note
    form_class = NoteForm
    template_name = 'notes/note_form.html'
    # success_url встановлюється в form_valid

    def get_context_data(self, **kwargs):
        # Додаємо порожній формсет для фото до контексту
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['photo_formset'] = NotePhotoFormSet(self.request.POST, self.request.FILES, prefix='photos')
        else:
            context['photo_formset'] = NotePhotoFormSet(prefix='photos')
        context['view_title'] = "Створити нову нотатку" # Додаємо заголовок для шаблону
        return context

    def form_valid(self, form):
        # Призначаємо користувача та обробляємо формсет
        context = self.get_context_data()
        photo_formset = context['photo_formset']
        form.instance.user = self.request.user # Призначаємо користувача

        # Використовуємо транзакцію, щоб або все збереглося, або нічого
        with transaction.atomic():
            self.object = form.save() # Зберігаємо основну нотатку
            if photo_formset.is_valid():
                photo_formset.instance = self.object # Прив'язуємо фото до створеної нотатки
                photo_formset.save() # Зберігаємо фотографії
                messages.success(self.request, "Нотатку та фото успішно створено!")
                return redirect(self.object.get_absolute_url()) # Перехід на деталі нотатки
            else:
                # Якщо формсет фото не валідний, транзакція відкотиться
                # і ми повернемо форму з помилками (хоча CreateView зазвичай не доходить сюди при невалідному головному form)
                # Краще додати обробку помилок фото_формсету в get_context_data або перевіряти тут
                 messages.error(self.request, "Помилка при збереженні фотографій.")
                 # Повертаємо форму з помилками (стандартна поведінка CreateView спрацює)
                 return self.form_invalid(form)


class NoteUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редагування існуючої нотатки та її фотографій."""
    model = Note
    form_class = NoteForm
    template_name = 'notes/note_form.html'
    # success_url встановлюється в form_valid або get_absolute_url моделі

    def test_func(self):
        # Перевірка, що користувач є власником нотатки
        note = self.get_object()
        return self.request.user == note.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            # Передаємо існуючий екземпляр нотатки до формсету
            context['photo_formset'] = NotePhotoFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix='photos')
        else:
            context['photo_formset'] = NotePhotoFormSet(instance=self.object, prefix='photos')
        context['view_title'] = "Редагувати нотатку" # Додаємо заголовок
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        photo_formset = context['photo_formset']

        if not photo_formset.is_valid():
             messages.error(self.request, "Будь ласка, виправте помилки у формі фотографій.")
             # Важливо: повертаємо невалідне відтворення форми, передаючи обидві форми
             # Ми не можемо просто викликати self.form_invalid(form), бо треба передати й photo_formset
             # Треба переконатись, що context містить і form, і photo_formset з помилками
             return self.render_to_response(self.get_context_data(form=form, photo_formset=photo_formset))


        with transaction.atomic():
            self.object = form.save() # Зберігаємо оновлену нотатку
            photo_formset.instance = self.object # Переприв'язуємо (про всяк випадок)
            photo_formset.save() # Зберігаємо зміни у фото (нові, змінені, видалені)

        messages.success(self.request, "Нотатку та фото успішно оновлено!")
        return redirect(self.object.get_absolute_url())

class NoteDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Видалення нотатки (фото видаляться каскадно)."""
    model = Note
    template_name = 'notes/note_confirm_delete.html'
    success_url = reverse_lazy('notes:note_list') # Куди перенаправити після видалення

    def test_func(self):
        # Перевірка, що користувач є власником нотатки
        note = self.get_object()
        return self.request.user == note.user

    def form_valid(self, form):
        # Додаємо повідомлення перед видаленням
        messages.success(self.request, f"Нотатку '{self.object.title}' успішно видалено.")
        return super().form_valid(form)
    
# --- VIEW ДЛЯ ЕКСПОРТУ ---
@login_required
def export_notes_json(request):
    """Експортує нотатки поточного користувача у форматі JSON."""
    notes = Note.objects.filter(user=request.user).prefetch_related('photos') # Оптимізація: завантажуємо фото одразу
    notes_data = []

    for note in notes:
        photos_list = []
        for photo in note.photos.all():
            photos_list.append({
                'image_url': request.build_absolute_uri(photo.image.url) if photo.image else None, # Повний URL до фото
                'caption': photo.caption,
                'uploaded_at': photo.uploaded_at.isoformat(), # Дата у стандартному форматі
            })

        notes_data.append({
            'date': note.date.isoformat(),
            'title': note.title,
            'content': note.content,
            'created_at': note.created_at.isoformat(),
            'updated_at': note.updated_at.isoformat(),
            'photos': photos_list, # Додаємо список фото
        })

    # Створюємо JSON-рядок
    json_data = json.dumps(notes_data, indent=2, ensure_ascii=False) # indent для краси, ensure_ascii для кирилиці

    # Готуємо відповідь для завантаження файлу
    response = HttpResponse(json_data, content_type='application/json; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="notes_export_{request.user.username}_{timezone.now().strftime("%Y%m%d")}.json"'
    return response

# --- VIEW ДЛЯ ІМПОРТУ ---
@login_required
def import_notes_json(request):
    """Імпортує нотатки з JSON файлу."""
    if request.method == 'POST':
        form = NoteImportForm(request.POST, request.FILES)
        if form.is_valid():
            json_file = request.FILES['json_file']
            try:
                # Читаємо файл і парсимо JSON
                data = json.load(json_file)
                if not isinstance(data, list):
                    raise ValueError("JSON файл має містити список (масив) об'єктів нотаток.")

                imported_count = 0
                skipped_count = 0
                error_list = []

                with transaction.atomic(): # Виконуємо все в одній транзакції
                    for index, note_data in enumerate(data):
                        try:
                            # Валідація базових полів
                            if not isinstance(note_data, dict):
                                raise ValueError(f"Запис #{index+1} не є словником.")
                            title = note_data.get('title')
                            content = note_data.get('content')
                            date_str = note_data.get('date')

                            if not all([title, content, date_str]):
                                raise ValueError(f"Запис #{index+1}: відсутні обов'язкові поля title, content або date.")

                            # Конвертуємо дату
                            try:
                                note_date = timezone.datetime.fromisoformat(date_str).date()
                            except ValueError:
                                raise ValueError(f"Запис #{index+1}: невірний формат дати '{date_str}'. Очікується YYYY-MM-DD.")

                            # Створюємо нотатку (можна додати перевірку на дублікати за бажанням)
                            note = Note.objects.create(
                                user=request.user,
                                date=note_date,
                                title=title,
                                content=content
                                # Дати created_at/updated_at встановляться автоматично
                            )
                            imported_count += 1

                            # Важливо: імпорт фото з JSON зазвичай не роблять напряму.
                            # Цей код імпортує тільки текстові дані нотаток.
                            # Якщо в JSON є інформація про фото, її можна логувати або ігнорувати.
                            if 'photos' in note_data:
                                # Можна додати логіку для обробки інформації про фото,
                                # але не самі файли фотографій.
                                pass # Поки ігноруємо

                        except ValueError as e:
                            skipped_count += 1
                            error_list.append(f"Помилка імпорту запису #{index+1}: {e}")
                        except Exception as e: # Ловимо інші можливі помилки
                             skipped_count += 1
                             error_list.append(f"Невідома помилка імпорту запису #{index+1}: {e}")
                             # Якщо помилка критична, можна перервати транзакцію
                             # raise # Розкоментуйте, щоб зупинити імпорт при першій серйозній помилці


                # Формуємо повідомлення
                if imported_count > 0:
                    messages.success(request, f"Успішно імпортовано {imported_count} нотаток.")
                if skipped_count > 0:
                    messages.warning(request, f"Пропущено {skipped_count} нотаток через помилки:")
                    for err in error_list[:5]: # Показуємо перші 5 помилок
                        messages.error(request, err)
                    if len(error_list) > 5:
                         messages.info(request, "...та інші.")

                return redirect('notes:note_list')

            except json.JSONDecodeError:
                messages.error(request, "Не вдалося прочитати JSON файл. Перевірте його формат.")
            except ValueError as e: # Ловимо помилки валідації структури JSON
                 messages.error(request, f"Помилка структури JSON: {e}")
            except Exception as e: # Загальний обробник помилок читання файлу
                messages.error(request, f"Виникла помилка при обробці файлу: {e}")
        else:
            # Якщо форма файлу не валідна (наприклад, файл не вибрано)
             messages.error(request, "Будь ласка, виберіть JSON файл для імпорту.")

    else: # GET request
        form = NoteImportForm()

    return render(request, 'notes/note_import.html', {'form': form})