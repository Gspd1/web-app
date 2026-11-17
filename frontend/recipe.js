
const API_URL = "http://127.0.0.1:8000";

// Получаем ID рецепта из адресной строки
const params = new URLSearchParams(window.location.search);
const recipeId = params.get("id");

// Загружаем рецепт
async function loadRecipe() {
    const nameElement = document.getElementById("recipe-name");
    const categoryElement = document.getElementById("recipe-category");
    const ingredientsList = document.getElementById("ingredients-list");
    const stepsList = document.getElementById("steps-list");

    if (!recipeId || !Number.isInteger(Number(recipeId)) || Number(recipeId) < 1) {
        nameElement.textContent = "Рецепт не выбран";
        ingredientsList.textContent = "";
        stepsList.textContent = "";
        return;
    }

    try {
        const response = await fetch(`${API_URL}/recipes/${recipeId}`);

        if (!response.ok) {
            throw new Error("Не удалось получить рецепт");
        }

        const data = await response.json();

        if (data.error) {
            nameElement.textContent = data.error;
            return;
        }

        // Название и категория
        document.title = data.recipe.name;
        nameElement.textContent = data.recipe.name;
        categoryElement.textContent = data.recipe.type_name;

        // Фотография рецепта
        const recipePhoto = document.getElementById("recipe-photo");

        if (data.recipe.image_path) {
            recipePhoto.src = `${API_URL}/${data.recipe.image_path}`;
            recipePhoto.hidden = false;
        }

        // Ингредиенты
        ingredientsList.innerHTML = "";

        data.ingredients.forEach(ingredient => {
            const li = document.createElement("li");

            let amount = "";

            if (ingredient.amount !== null) {
                amount = `${ingredient.amount} ${ingredient.unit || ""}`;
            }

            li.textContent = amount
                ? `${ingredient.name} — ${amount}`
                : ingredient.name;

            ingredientsList.appendChild(li);
        });

        if (data.ingredients.length === 0) {
            ingredientsList.textContent = "Ингредиенты пока не добавлены.";
        }

        // Шаги приготовления
        stepsList.innerHTML = "";

        data.steps.forEach(step => {
            const stepDiv = document.createElement("div");
            stepDiv.className = "step";

            const heading = document.createElement("h3");
            heading.textContent = `Шаг ${step.recipe_step_number}`;

            const description = document.createElement("p");
            description.textContent = step.recipe_step_description;

            stepDiv.appendChild(heading);
            stepDiv.appendChild(description);

            if (step.recipe_step_image) {
                const image = document.createElement("img");
                image.src = `${API_URL}/${step.recipe_step_image}`;
                image.alt = `Шаг ${step.recipe_step_number}`;
                stepDiv.appendChild(image);
            }

            stepsList.appendChild(stepDiv);
        });

        if (data.steps.length === 0) {
            stepsList.textContent = "Шаги приготовления пока не добавлены.";
        }

        updateFavoriteButton();

    } catch (error) {
        console.error(error);
        nameElement.textContent = "Не удалось загрузить рецепт.";
        ingredientsList.textContent = "";
        stepsList.textContent = "";
    }
}


// Получаем список избранного из браузера
function getFavorites() {
    return JSON.parse(localStorage.getItem("favorites")) || [];
}


// Обновляем надпись на кнопке
function updateFavoriteButton() {
    const button = document.getElementById("favorite-button");
    const favorites = getFavorites();

    if (favorites.includes(Number(recipeId))) {
        button.textContent = "Удалить из избранного";
    } else {
        button.textContent = "Добавить в избранное";
    }
}


// Добавляем или удаляем рецепт из избранного
document.getElementById("favorite-button").addEventListener("click", function () {
    const favorites = getFavorites();
    const id = Number(recipeId);

    if (favorites.includes(id)) {
        const index = favorites.indexOf(id);
        favorites.splice(index, 1);
    } else {
        favorites.push(id);
    }

    localStorage.setItem("favorites", JSON.stringify(favorites));

    updateFavoriteButton();
});


// Запускаем загрузку рецепта
loadRecipe();
