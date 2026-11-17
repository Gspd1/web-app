from fastapi import FastAPI, Query
from database import get_connection
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

# Путь к папке с изображениями
BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "images"

# Разрешаем браузеру получать изображения
app.mount(
    "/images",
    StaticFiles(directory=IMAGES_DIR),
    name="images"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Главная страница для проверки работы сервера
@app.get("/")
def home():
    return {"message": "Сервер работает!"}


# Получение всех категорий рецептов
@app.get("/recipe-types")
def get_recipe_types():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM recipe_type ORDER BY id;")
    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return [dict(row) for row in result]


# Получение всех ингредиентов
@app.get("/ingredients")
def get_ingredients():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            ingredients.id,
            ingredients.name,
            ingredients.type_id,
            ingredients_type.name AS type_name
        FROM ingredients
        JOIN ingredients_type
            ON ingredients.type_id = ingredients_type.id
        ORDER BY ingredients.id;
    """)

    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return [dict(row) for row in result]


# Получение всех рецептов
@app.get("/recipes")
def get_recipes():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            recipe.id,
            recipe.name,
            recipe.type_id,
            recipe_type.name AS type_name,
            recipe.image_path
        FROM recipe
        JOIN recipe_type
            ON recipe.type_id = recipe_type.id
        ORDER BY recipe.id;
    """)

    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return [dict(row) for row in result]



# Поиск рецептов по категориям и ингредиентам
@app.get("/search")
def search_recipes(
    category_ids: list[int] = Query(default=[]),
    ingredient_ids: list[int] = Query(default=[])
):
    connection = get_connection()
    cursor = connection.cursor()

    # Основной SQL-запрос
    sql = """
        SELECT
            recipe.id,
            recipe.name,
            recipe.type_id,
            recipe_type.name AS type_name,
            recipe.image_path
        FROM recipe
        JOIN recipe_type
            ON recipe.type_id = recipe_type.id
        WHERE 1 = 1
    """

    parameters = []

    # Фильтр по категориям
    if category_ids:
        sql += " AND recipe.type_id = ANY(%s)"
        parameters.append(category_ids)

    # Фильтр по ингредиентам
    if ingredient_ids:
        sql += """
            AND recipe.id IN (
                SELECT recipe_id
                FROM ingredients_recipes
                WHERE ingredients_id = ANY(%s)
                GROUP BY recipe_id
                HAVING COUNT(DISTINCT ingredients_id) = %s
            )
        """
        parameters.append(ingredient_ids)
        parameters.append(len(ingredient_ids))

    sql += " ORDER BY recipe.id;"

    cursor.execute(sql, parameters)
    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return [dict(row) for row in result]



# Получение полной информации об одном рецепте
@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    # Получаем основную информацию о рецепте
    cursor.execute("""
        SELECT
            recipe.id,
            recipe.name,
            recipe.image_path,
            recipe_type.name AS type_name
        FROM recipe
        JOIN recipe_type
            ON recipe.type_id = recipe_type.id
        WHERE recipe.id = %s;
    """, (recipe_id,))

    recipe = cursor.fetchone()

    if recipe is None:
        cursor.close()
        connection.close()
        return {"error": "Рецепт не найден"}

    # Получаем ингредиенты рецепта
    cursor.execute("""
        SELECT
            ingredients.name,
            ingredients_recipes.amount,
            ingredients_recipes.unit
        FROM ingredients_recipes
        JOIN ingredients
            ON ingredients_recipes.ingredients_id = ingredients.id
        WHERE ingredients_recipes.recipe_id = %s
        ORDER BY ingredients.name;
    """, (recipe_id,))

    ingredients = cursor.fetchall()

    # Получаем шаги приготовления
    cursor.execute("""
        SELECT
            recipe_step_number,
            recipe_step_description,
            recipe_step_image
        FROM recipe_step
        WHERE recipe_id = %s
        ORDER BY recipe_step_number;
    """, (recipe_id,))

    steps = cursor.fetchall()

    cursor.close()
    connection.close()

    return {
        "recipe": dict(recipe),
        "ingredients": [dict(row) for row in ingredients],
        "steps": [dict(row) for row in steps]
    }
