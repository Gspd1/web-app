const API_URL = "http://127.0.0.1:8000";

// Загружаем категории и ингредиенты при открытии страницы
async function loadFilters() {
    try {
        const [categoriesResponse, ingredientsResponse] = await Promise.all([
            fetch(`${API_URL}/recipe-types`),
            fetch(`${API_URL}/ingredients`)
        ]);

        if (!categoriesResponse.ok || !ingredientsResponse.ok) {
            throw new Error("Не удалось загрузить фильтры");
        }

        const categories = await categoriesResponse.json();
        const ingredients = await ingredientsResponse.json();

        showCategories(categories);
        showIngredients(ingredients);

    } catch (error) {
        console.error("Ошибка загрузки фильтров:", error);

        document.getElementById("category-filters").textContent =
            "Не удалось загрузить категории.";

        document.getElementById("ingredient-filters").textContent =
            "Не удалось загрузить ингредиенты.";
    }
}


// Отображаем категории
function showCategories(categories) {
    const container = document.getElementById("category-filters");

    container.innerHTML = "";

    categories.forEach(category => {
        const label = document.createElement("label");
        label.className = "filter-option";

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.name = "category";
        checkbox.value = category.id;

        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(" " + category.name));

        container.appendChild(label);
    });
}


// Отображаем ингредиенты, разделённые по группам
function showIngredients(ingredients) {
    const container = document.getElementById("ingredient-filters");

    container.innerHTML = "";

    const groups = new Map();

    ingredients.forEach(ingredient => {
        if (!groups.has(ingredient.type_name)) {
            groups.set(ingredient.type_name, []);
        }

        groups.get(ingredient.type_name).push(ingredient);
    });

    groups.forEach((groupIngredients, groupName) => {
        const heading = document.createElement("h3");
        heading.textContent = groupName;

        container.appendChild(heading);

        groupIngredients.forEach(ingredient => {
            const label = document.createElement("label");
            label.className = "filter-option";

            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.name = "ingredient";
            checkbox.value = ingredient.id;

            label.appendChild(checkbox);
            label.appendChild(
                document.createTextNode(" " + ingredient.name)
            );

            container.appendChild(label);
        });
    });
}


// Выполняем поиск рецептов
async function searchRecipes(event) {
    event.preventDefault();

    const recipeList = document.getElementById("recipe-list");

    recipeList.textContent = "Ищем рецепты...";

    // Получаем выбранные категории
    const selectedCategories = document.querySelectorAll(
        'input[name="category"]:checked'
    );

    // Получаем выбранные ингредиенты
    const selectedIngredients = document.querySelectorAll(
        'input[name="ingredient"]:checked'
    );

    // Создаём параметры запроса
    const params = new URLSearchParams();

    selectedCategories.forEach(checkbox => {
        params.append("category_ids", checkbox.value);
    });

    selectedIngredients.forEach(checkbox => {
        params.append("ingredient_ids", checkbox.value);
    });

    try {
        const response = await fetch(`${API_URL}/search?${params.toString()}`);

        if (!response.ok) {
            throw new Error("Ошибка поиска рецептов");
        }

        const recipes = await response.json();

        showRecipes(recipes);

    } catch (error) {
        console.error("Ошибка поиска:", error);

        recipeList.textContent =
            "Не удалось выполнить поиск. Проверьте работу сервера.";
    }
}


// Отображаем найденные рецепты
function showRecipes(recipes) {
    const recipeList = document.getElementById("recipe-list");

    recipeList.innerHTML = "";

    if (recipes.length === 0) {
        recipeList.textContent = "По вашему запросу ничего не найдено.";
        return;
    }

    recipes.forEach(recipe => {
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
}


// Подключаем обработчик кнопки поиска
document.getElementById("search-form").addEventListener(
    "submit",
    searchRecipes
);


// Загружаем фильтры при открытии страницы
loadFilters();