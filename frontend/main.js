
const API_URL = "http://127.0.0.1:8000";

// Получаем список рецептов с сервера
async function loadRecipes() {
    const recipeList = document.getElementById("recipe-list");

    try {
        const response = await fetch(`${API_URL}/recipes`);

        if (!response.ok) {
            throw new Error("Не удалось получить рецепты");
        }

        const recipes = await response.json();

        // Очищаем контейнер
        recipeList.innerHTML = "";

        if (recipes.length === 0) {
            recipeList.textContent = "Пока рецептов нет.";
            return;
        }

        // Создаём карточку для каждого рецепта
        recipes.forEach(recipe => {
            const card = document.createElement("a");

            card.className = "recipe-card";
            card.href = `recipe.html?id=${encodeURIComponent(recipe.id)}`;

            // Добавляем фотографию, если она указана в базе
            if (recipe.image_path) {
                const image = document.createElement("img");

                image.src = `${API_URL}/${recipe.image_path}`;
                image.alt = recipe.name;

                // Если файл фотографии пока отсутствует,
                // просто скрываем сломанную картинку
                image.onerror = function () {
                    image.remove();
                };

                card.appendChild(image);
            }

            // Добавляем название рецепта
            const title = document.createElement("h3");
            title.textContent = recipe.name;

            card.appendChild(title);

            // Добавляем готовую карточку на страницу
            recipeList.appendChild(card);
        });

    } catch (error) {
        console.error("Ошибка загрузки рецептов:", error);
        recipeList.textContent =
            "Не удалось загрузить рецепты. Проверьте работу сервера.";
    }
}

// Запускаем загрузку при открытии страницы
loadRecipes();
