document.addEventListener('DOMContentLoaded', function() {
    try {
        const labelsElement = document.getElementById('chart-labels-data');
        const dataElement = document.getElementById('chart-data-data');

        if (!labelsElement || !dataElement) {
            console.error("Не вдалося знайти елементи даних для діаграми (chart-labels-data або chart-data-data).");
            return;
        }

        // Отримуємо JSON рядки з textContent
        const labelsJsonString = labelsElement.textContent;
        const dataJsonString = dataElement.textContent;
        console.log("Рядок JSON з textContent для labels:", labelsJsonString);
        console.log("Рядок JSON з textContent для data:", dataJsonString);

        // --- ПОДВІЙНИЙ ПАРСИНГ ---
        // Перший парсинг (очікуємо отримати рядок, що виглядає як JSON)
        const intermediateLabels = JSON.parse(labelsJsonString);
        const intermediateData = JSON.parse(dataJsonString);
        console.log("Результат першого парсингу labels:", intermediateLabels, typeof intermediateLabels);
        console.log("Результат першого парсингу data:", intermediateData, typeof intermediateData);

        // Другий парсинг (парсимо рядок, отриманий на першому кроці)
        const labels = JSON.parse(intermediateLabels);
        const data = JSON.parse(intermediateData);
        // --- КІНЕЦЬ ПОДВІЙНОГО ПАРСИНГУ ---

        // Логуємо фінальний результат
        console.log("Розпарсені labels (фінал):", labels);
        console.log("Тип labels (фінал):", typeof labels, ", Це масив?", Array.isArray(labels));
        console.log("Розпарсені data (фінал):", data);
        console.log("Тип data (фінал):", typeof data, ", Це масив?", Array.isArray(data));

        // Перевірка, чи отримали масиви
        if (!Array.isArray(labels) || !Array.isArray(data)) {
                console.error("Дані все ще не є масивами після подвійного парсингу!");
                return; // Зупиняємо, якщо щось пішло не так
        }

        // ... решта коду для створення Chart ...

        const ctx = document.getElementById('expenseCategoryChart').getContext('2d');
        const expenseCategoryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels, // Передаємо розпарсений масив
                datasets: [{
                    label: 'Витрати за категоріями',
                    data: data, // Передаємо розпарсений масив
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.7)', 'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 206, 86, 0.7)', 'rgba(75, 192, 192, 0.7)',
                        'rgba(153, 102, 255, 0.7)', 'rgba(255, 159, 64, 0.7)',
                        'rgba(199, 199, 199, 0.7)', 'rgba(184, 211, 32, 0.7)',
                        'rgba(99, 255, 133, 0.7)', 'rgba(86, 14, 202, 0.7)',
                        'rgba(69, 5, 245, 0.7)', 'rgba(8, 8, 8, 0.7)',
                        'rgba(245, 5, 17, 0.97)', 'rgba(246, 250, 19, 0.95)',
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)', 'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)', 'rgba(255, 159, 64, 1)',
                        'rgba(199, 199, 199, 1)', 'rgba(184, 211, 32, 0.7)',
                        'rgba(99, 255, 133, 0.7)', 'rgba(86, 14, 202, 0.7)',
                        'rgba(69, 5, 245, 0.7)', 'rgba(8, 8, 8, 0.7)',
                        'rgba(245, 5, 17, 0.97)', 'rgba(246, 250, 19, 0.95)',
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top', },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                if (label) { label += ': '; }
                                if (context.parsed !== null) {
                                    label += context.parsed.toFixed(2) + ' грн';
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });
    } catch (e) {
         console.error("Помилка під час ініціалізації діаграми:", e);
    }
});