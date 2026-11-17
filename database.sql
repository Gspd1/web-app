
-- Категории ингредиентов
CREATE TABLE ingredients_type (
    id SERIAL PRIMARY KEY,
    name VARCHAR(30) UNIQUE NOT NULL
);

-- Ингредиенты
CREATE TABLE ingredients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    type_id INTEGER NOT NULL
        REFERENCES ingredients_type(id)
        ON DELETE RESTRICT
);

-- Категории рецептов
CREATE TABLE recipe_type (
    id SERIAL PRIMARY KEY,
    name VARCHAR(30) UNIQUE NOT NULL
);

-- Рецепты
CREATE TABLE recipe (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    type_id INTEGER NOT NULL
        REFERENCES recipe_type(id)
        ON DELETE RESTRICT,
    image_path TEXT
);

-- Ингредиенты конкретных рецептов
CREATE TABLE ingredients_recipes (
    ingredients_id INTEGER
        REFERENCES ingredients(id) ON DELETE CASCADE,
    recipe_id INTEGER
        REFERENCES recipe(id) ON DELETE CASCADE,
    amount NUMERIC(10, 2),
    unit VARCHAR(30),
    PRIMARY KEY (ingredients_id, recipe_id)
);

-- Шаги приготовления
CREATE TABLE recipe_step (
    recipe_id INTEGER
        REFERENCES recipe(id) ON DELETE CASCADE,
    recipe_step_number INTEGER NOT NULL,
    recipe_step_description TEXT NOT NULL,
    recipe_step_image TEXT,
    PRIMARY KEY (recipe_id, recipe_step_number)
);
