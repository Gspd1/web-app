const API_URL = "http://127.0.0.1:8000";

// Получаем сохранённые ID рецептов
function getFavorites() {
    return JSON.parse(localStorage.getItem("favorites")) || [];
}

// Загружаем рецепты из базы данных
async function loadFavorites() {
    const recipeList = document.getElementById("recipe-list");

    try {
        const response = await fetch(`${API_URL}/recipes`);

        if (!response.ok) {
            throw new Error("Не удалось получить рецепты");
        }

        const recipes = await response.json();
        const favoriteIds = getFavorites();

        // Оставляем только рецепты, которые есть в избранном
        const favoriteRecipes = recipes.filter(recipe =>
            favoriteIds.includes(Number(recipe.id))
        );

        recipeList.innerHTML = "";

        if (favoriteRecipes.length === 0) {
            recipeList.textContent = "В избранном пока нет рецептов.";
            return;
        }

        // Создаём карточку для каждого избранного рецепта
        favoriteRecipes.forEach(recipe => {
            const card = document.createElement("a");
            card.className = "recipe-card";
            card.href = `recipe.html?id=${recipe.id}`;

            if (recipe.image_path) {
                const image = document.createElement("img");
                image.src = `${API_URL}/${recipe.image_path}`;
                image.alt = recipe.name;

                image.onerror = function () {
                    image.remove();
                };

                card.appendChild(image);
            }

            const title = document.createElement("h3");
            title.textContent = recipe.name;

            card.appendChild(title);
            recipeList.appendChild(card);
        });

    } catch (error) {
        console.error("Ошибка загрузки избранного:", error);
        recipeList.textContent =
            "Не удалось загрузить избранное. Проверьте работу сервера.";
    }
}

loadFavorites();