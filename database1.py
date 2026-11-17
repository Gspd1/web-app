import psycopg2 as ps

connection = ps.connect(
    host='your_actual_host',
    user='your_actual_user',
    password='your_actual_password',
    database='your_actual_database'
)
cursor = connection.cursor()


# recipe_type = """CREATE TABLE IF NOT EXISTS recipe_type (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(255) NOT NULL UNIQUE
# );"""
#
#
# ingredients_type= """CREATE TABLE IF NOT EXISTS ingredients_type (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(255) NOT NULL UNIQUE
# );"""
#
#
# ingredients = """CREATE TABLE IF NOT EXISTS ingredients (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(255) NOT NULL UNIQUE,
#     type_id INTEGER NOT NULL,
#     FOREIGN KEY (type_id) REFERENCES ingredients_type(id) ON DELETE RESTRICT
# );"""
#
#
# recipe = """CREATE TABLE IF NOT EXISTS recipe (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(255) NOT NULL,
#     type_id INTEGER NOT NULL,
#     FOREIGN KEY (type_id) REFERENCES recipe_type(id) ON DELETE RESTRICT
# );"""
#
#
# recipe_step = """CREATE TABLE IF NOT EXISTS recipe_step (
#     id SERIAL PRIMARY KEY,
#     recipe_id INTEGER NOT NULL,
#     step_number INTEGER NOT NULL,
#     description TEXT NOT NULL,
#     image VARCHAR(512),
#     FOREIGN KEY (recipe_id) REFERENCES recipe(id) ON DELETE CASCADE
# );"""
#
#
# ingredients_recipes = """CREATE TABLE IF NOT EXISTS ingredients_recipes (
#     recipe_id INTEGER NOT NULL,
#     ingredient_id INTEGER NOT NULL,
#     PRIMARY KEY (recipe_id, ingredient_id),
#     FOREIGN KEY (recipe_id) REFERENCES recipe(id) ON DELETE CASCADE,
#     FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
# );"""
#
#
# favorites = """CREATE TABLE IF NOT EXISTS favorites (
#     recipe_id INTEGER PRIMARY KEY,
#     FOREIGN KEY (recipe_id) REFERENCES recipe(id) ON DELETE CASCADE
# );"""
#
#
# try:
#     cursor.execute(recipe_type)
#     cursor.execute(ingredients_type)
#     cursor.execute(ingredients)
#     cursor.execute(recipe)
#     cursor.execute(recipe_step)
#     cursor.execute(ingredients_recipes)
#     cursor.execute(favorites)
#
#
#     connection.commit()
#     print("Все таблицы успешно созданы!")
#
# except Exception as e:
#     connection.rollback()
#     print(f"Произошла ошибка при создании таблиц: {e}")
#
# finally:
#     cursor.close()
#     connection.close()
