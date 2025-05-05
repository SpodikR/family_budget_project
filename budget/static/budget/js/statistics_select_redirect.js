// budget/static/budget/js/statistics_select_redirect.js
document.addEventListener('DOMContentLoaded', function() {
    const monthSelect = document.getElementById('month_select');
    if (monthSelect) {
        monthSelect.addEventListener('change', function() {
            console.log("Зміна month_select, поточне значення:", this.value);
            if (this.value) {
                if (typeof this.value === 'string' && this.value.startsWith('/')) {
                     console.log("Перенаправлення на:", this.value);
                     window.location.href = this.value; // Перенаправляємо
                } else {
                     console.error("Значення для перенаправлення не є коректним URL:", this.value);
                }
            } else {
                console.error("Значення для перенаправлення порожнє!");
            }
        });
    } else {
         console.error("Елемент #month_select не знайдено!");
    }
});