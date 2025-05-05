// budget/static/budget/js/lightbox_init.js
window.addEventListener('load', function() {
    console.log("Ініціалізація baguetteBox запущена! (з окремого файлу)");
  
    // Ініціалізуємо для чеків
    const checkGalleries = document.querySelectorAll('.checks-gallery');
    console.log("Знайдено галерей чеків:", checkGalleries.length);
    if (checkGalleries.length > 0) {
        try {
            baguetteBox.run('.checks-gallery', { /* options */ });
            console.log("baguetteBox.run('.checks-gallery') виконано.");
        } catch (e) {
            console.error("Помилка при запуску baguetteBox для чеків:", e);
        }
    }
  
    // Ініціалізуємо для фото нотаток
    const notePhotoGalleries = document.querySelectorAll('.notes-photo-gallery');
    console.log("Знайдено галерей фото нотаток:", notePhotoGalleries.length);
    if (notePhotoGalleries.length > 0) {
         try {
            baguetteBox.run('.notes-photo-gallery', {
                captions: function(element) {
                   return element.getAttribute('data-caption');
               }
            });
            console.log("baguetteBox.run('.notes-photo-gallery') виконано.");
        } catch (e) {
            console.error("Помилка при запуску baguetteBox для нотаток:", e);
        }
    }
  });