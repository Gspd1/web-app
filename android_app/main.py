from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.network.urlrequest import UrlRequest
from kivy.uix.image import AsyncImage
from kivy.storage.jsonstore import JsonStore
from kivy.uix.togglebutton import ToggleButton
from urllib.parse import urlencode


# Размер окна для разработки на компьютере
Window.size = (400, 700)

# Цвет фона приложения
Window.clearcolor = (0.89, 0.86, 0.83, 1)


# Создание скруглённого контейнера
def create_container(layout, color):
    with layout.canvas.before:
        Color(*color)
        layout.background = RoundedRectangle(
            pos=layout.pos,
            size=layout.size,
            radius=[15]
        )

    layout.bind(
        pos=lambda instance, value:
        setattr(layout.background, "pos", value),

        size=lambda instance, value:
        setattr(layout.background, "size", value)
    )


# Оформление обычных кнопок
def style_button(button, color=(0.79, 0.60, 0.29, 1)):
    with button.canvas.before:
        Color(*color)
        button.bg = RoundedRectangle(
            pos=button.pos,
            size=button.size,
            radius=[12]
        )

    button.bind(
        pos=lambda instance, value:
        setattr(button.bg, "pos", value),

        size=lambda instance, value:
        setattr(button.bg, "size", value)
    )

    # Убираем стандартный квадратный фон Kivy
    button.background_color = (0, 0, 0, 0)
    button.background_normal = ""
    button.background_down = ""

    button.color = (0.13, 0.09, 0.05, 1)


# Оформление переключателей категорий и ингредиентов
def style_toggle(button):
    with button.canvas.before:
        button.bg_color = Color(0.89, 0.86, 0.83, 1)

        button.bg = RoundedRectangle(
            pos=button.pos,
            size=button.size,
            radius=[7]
        )

    button.bind(
        pos=lambda instance, value:
        setattr(button.bg, "pos", value),

        size=lambda instance, value:
        setattr(button.bg, "size", value)
    )

    button.background_normal = ""
    button.background_down = ""
    button.background_color = (0, 0, 0, 0)


# Экраны приложения
class MainScreen(Screen):
    pass


class RecipeScreen(Screen):
    pass


class FavoriteScreen(Screen):
    pass


class SearchScreen(Screen):
    pass


class RecipeApp(App):

    # Создание карточки рецепта
    def create_recipe_card(self, recipe):
        card = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=200,
            padding=8,
            spacing=5
        )

        create_container(card, (0.49, 0.34, 0.13, 1))

        # Фотография рецепта
        recipe_image = AsyncImage(
            source="http://127.0.0.1:8000/" + recipe["image_path"],
            size_hint=(1, 0.8),
            allow_stretch=True,
            keep_ratio=False
        )

        # Название рецепта
        recipe_name = Label(
            text=recipe["name"],
            font_size=15,
            color=(1, 1, 1, 1),
            size_hint=(1, 0.2),
            halign="center",
            valign="middle"
        )

        recipe_name.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", value)
        )

        card.add_widget(recipe_image)
        card.add_widget(recipe_name)

        # Открываем рецепт при нажатии на карточку
        card.bind(
            on_touch_down=lambda instance, touch,
            recipe_id=recipe["id"]:
            self.open_recipe(recipe_id)
            if instance.collide_point(*touch.pos)
            else None
        )

        return card

    # Загрузка отдельного рецепта
    def open_recipe(self, recipe_id):
        UrlRequest(
            f"http://127.0.0.1:8000/recipes/{recipe_id}",
            on_success=self.recipe_details_loaded,
            on_error=self.request_error,
            on_failure=self.request_error
        )

    # Отображение страницы рецепта
    def recipe_details_loaded(self, request, data):

        recipe = data["recipe"]
        ingredients = data["ingredients"]

        self.recipe_screen.clear_widgets()

        scroll = ScrollView()

        recipe_layout = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10,
            size_hint_y=None
        )

        recipe_layout.bind(
            minimum_height=recipe_layout.setter("height")
        )

        # Кнопка возврата
        back_button = Button(
            text="Назад",
            size_hint_y=None,
            height=45
        )

        style_button(back_button)

        back_button.bind(
            on_release=lambda instance:
            setattr(self.screen_manager, "current", "main")
        )

        recipe_layout.add_widget(back_button)

        # Название блюда
        title = Label(
            text=recipe["name"],
            font_size=24,
            color=(0.13, 0.09, 0.05, 1),
            size_hint_y=None,
            height=50
        )

        recipe_layout.add_widget(title)

        # Фотография блюда
        recipe_image = AsyncImage(
            source="http://127.0.0.1:8000/" + recipe["image_path"],
            size_hint_y=None,
            height=200,
            allow_stretch=True,
            keep_ratio=False
        )

        recipe_layout.add_widget(recipe_image)

        # Кнопка добавления в избранное
        favorite_button = Button(
            text="Удалить из избранного"
            if self.favorites_store.exists(str(recipe["id"]))
            else "Добавить в избранное",
            size_hint_y=None,
            height=45,
            font_size=16
        )

        style_button(favorite_button)

        favorite_button.bind(
            on_release=lambda instance:
            self.toggle_favorite(recipe["id"], instance)
        )

        recipe_layout.add_widget(favorite_button)

        # Заголовок ингредиентов
        ingredients_title = Label(
            text="Ингредиенты",
            font_size=20,
            color=(0.13, 0.09, 0.05, 1),
            size_hint_y=None,
            height=40
        )

        recipe_layout.add_widget(ingredients_title)

        # Список ингредиентов
        for ingredient in ingredients:

            ingredient_label = Label(
                text=f'{ingredient["name"]} — '
                     f'{ingredient["amount"]} '
                     f'{ingredient["unit"]}',
                font_size=16,
                color=(0.13, 0.09, 0.05, 1),
                size_hint_y=None,
                height=30
            )

            recipe_layout.add_widget(ingredient_label)

        # Заголовок приготовления
        steps_title = Label(
            text="Приготовление",
            font_size=20,
            color=(0.13, 0.09, 0.05, 1),
            size_hint_y=None,
            height=45
        )

        recipe_layout.add_widget(steps_title)

        # Шаги приготовления
        for step in data["steps"]:

            step_label = Label(
                text=f'{step["recipe_step_number"]}. '
                     f'{step["recipe_step_description"]}',
                font_size=16,
                color=(0.13, 0.09, 0.05, 1),
                size_hint_y=None,
                height=80,
                halign="left",
                valign="middle"
            )

            step_label.bind(
                width=lambda instance, value:
                setattr(instance, "text_size", (value, None))
            )

            recipe_layout.add_widget(step_label)

            # Фотография шага, если она есть
            if step["recipe_step_image"] is not None:

                step_image = AsyncImage(
                    source="http://127.0.0.1:8000/"
                           + step["recipe_step_image"],
                    size_hint_y=None,
                    height=160,
                    allow_stretch=True,
                    keep_ratio=False
                )

                recipe_layout.add_widget(step_image)

        scroll.add_widget(recipe_layout)

        self.recipe_screen.add_widget(scroll)

        self.screen_manager.current = "recipe"

    # Загрузка рецептов при запуске
    def on_start(self):

        UrlRequest(
            "http://127.0.0.1:8000/recipes",
            on_success=self.recipes_loaded,
            on_error=self.request_error,
            on_failure=self.request_error
        )

    # Добавление и удаление из избранного
    def toggle_favorite(self, recipe_id, button):

        key = str(recipe_id)

        if self.favorites_store.exists(key):

            self.favorites_store.delete(key)

            button.text = "Добавить в избранное"

            print("Рецепт удалён из избранного")

        else:

            self.favorites_store.put(
                key,
                recipe_id=recipe_id
            )

            button.text = "Удалить из избранного"

            print("Рецепт добавлен в избранное")

    # Отображение избранного
    def show_favorites(self):

        self.favorite_screen.clear_widgets()

        layout = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        # Заголовок
        title = Label(
            text="Избранное",
            font_size=24,
            color=(0.13, 0.09, 0.05, 1),
            size_hint_y=None,
            height=50
        )

        layout.add_widget(title)

        # Кнопка возврата
        back_button = Button(
            text="Все рецепты",
            size_hint_y=None,
            height=45
        )

        style_button(back_button)

        back_button.bind(
            on_release=lambda instance:
            setattr(self.screen_manager, "current", "main")
        )

        layout.add_widget(back_button)

        # Прокручиваемая область
        scroll = ScrollView(
            do_scroll_x=False
        )

        recipes_layout = GridLayout(
            cols=2,
            spacing=12,
            padding=5,
            size_hint_x=1,
            size_hint_y=None
        )

        recipes_layout.bind(
            minimum_height=recipes_layout.setter("height")
        )

        # Получаем ID избранных рецептов
        favorite_ids = [
            int(key) for key in self.favorites_store.keys()
        ]

        # Показываем избранные рецепты
        found_favorites = False

        for recipe in self.recipes:

            if recipe["id"] in favorite_ids:

                card = self.create_recipe_card(recipe)

                recipes_layout.add_widget(card)

                found_favorites = True

        if not found_favorites:

            empty_label = Label(
                text="В избранном пока нет рецептов",
                color=(0.13, 0.09, 0.05, 1),
                size_hint_y=None,
                height=60
            )

            recipes_layout.add_widget(empty_label)

        scroll.add_widget(recipes_layout)

        layout.add_widget(scroll)

        self.favorite_screen.add_widget(layout)

        self.screen_manager.current = "favorites"

    # Открытие расширенного поиска
    def show_search(self):

        self.selected_category_ids = set()
        self.selected_ingredient_ids = set()

        self.search_screen.clear_widgets()

        scroll = ScrollView(
            do_scroll_x=False
        )

        content = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=12,
            size_hint_y=None,
            size_hint_x=1
        )

        content.bind(
            minimum_height=content.setter("height")
        )

        # Заголовок страницы
        title = Label(
            text="Расширенный поиск",
            font_size=24,
            bold=True,
            color=(0.13, 0.09, 0.05, 1),
            size_hint_y=None,
            height=55
        )

        content.add_widget(title)

        # Кнопка возврата
        back_button = Button(
            text="Все рецепты",
            size_hint_y=None,
            height=45
        )

        style_button(back_button)

        back_button.bind(
            on_release=lambda instance:
            setattr(self.screen_manager, "current", "main")
        )

        content.add_widget(back_button)

        # Контейнер формы поиска
        form_box = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10,
            size_hint_y=None
        )

        form_box.bind(
            minimum_height=form_box.setter("height")
        )

        create_container(
            form_box,
            (0.79, 0.60, 0.29, 1)
        )

        # Категории
        categories_title = Label(
            text="Категории",
            font_size=23,
            bold=True,
            color=(0.13, 0.09, 0.05, 1),
            size_hint_y=None,
            height=45,
            halign="left"
        )

        form_box.add_widget(categories_title)

        self.categories_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=5
        )

        self.categories_box.bind(
            minimum_height=self.categories_box.setter("height")
        )

        form_box.add_widget(self.categories_box)

        # Ингредиенты
        ingredients_title = Label(
            text="Ингредиенты",
            font_size=23,
            bold=True,
            color=(0.13, 0.09, 0.05, 1),
            size_hint_y=None,
            height=45,
            halign="left"
        )

        form_box.add_widget(ingredients_title)

        self.ingredients_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=5
        )

        self.ingredients_box.bind(
            minimum_height=self.ingredients_box.setter("height")
        )

        form_box.add_widget(self.ingredients_box)

        # Кнопка поиска
        find_button = Button(
            text="Найти рецепты",
            size_hint_y=None,
            height=50,
            font_size=17
        )

        style_button(
            find_button,
            color=(0.49, 0.34, 0.13, 1)
        )

        find_button.bind(
            on_release=lambda instance:
            self.search_recipes()
        )

        form_box.add_widget(find_button)

        content.add_widget(form_box)

        # Заголовок результатов
        results_title = Label(
            text="Результаты поиска",
            font_size=21,
            bold=True,
            color=(0.13, 0.09, 0.05, 1),
            size_hint_y=None,
            height=50
        )

        content.add_widget(results_title)

        # Сетка результатов — две карточки в ряд
        self.search_results_layout = GridLayout(
            cols=2,
            spacing=12,
            padding=5,
            size_hint_x=1,
            size_hint_y=None
        )

        self.search_results_layout.bind(
            minimum_height=
            self.search_results_layout.setter("height")
        )

        content.add_widget(self.search_results_layout)

        scroll.add_widget(content)

        self.search_screen.add_widget(scroll)

        self.screen_manager.current = "search"

        # Загружаем категории из базы
        UrlRequest(
            "http://127.0.0.1:8000/recipe-types",
            on_success=self.categories_loaded,
            on_error=self.request_error,
            on_failure=self.request_error
        )

        # Загружаем ингредиенты из базы
        UrlRequest(
            "http://127.0.0.1:8000/ingredients",
            on_success=self.ingredients_loaded,
            on_error=self.request_error,
            on_failure=self.request_error
        )

    # Изменение выбранных фильтров
    def update_selection(self, selected_ids, item_id, active):

        if active:
            selected_ids.add(item_id)
        else:
            selected_ids.discard(item_id)

    # Изменение внешнего вида переключателя
    def update_filter_toggle(
        self,
        button,
        state,
        selected_ids,
        item_id
    ):

        self.update_selection(
            selected_ids,
            item_id,
            state == "down"
        )

        if state == "down":

            button.text = "✓"

            button.bg_color.rgba = (0.49, 0.34, 0.13, 1)

            button.color = (1, 1, 1, 1)

        else:

            button.text = ""

            button.bg_color.rgba = (0.89, 0.86, 0.83, 1)

            button.color = (0.13, 0.09, 0.05, 1)

    # Загрузка категорий
    def categories_loaded(self, request, data):

        self.categories_box.clear_widgets()

        for category in data:

            row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=42,
                spacing=12
            )

            checkbox = ToggleButton(
                text="",
                size_hint=(None, None),
                size=(28, 28)
            )

            style_toggle(checkbox)

            checkbox.bind(
                state=lambda instance, value,
                item_id=category["id"]:
                self.update_filter_toggle(
                    instance,
                    value,
                    self.selected_category_ids,
                    item_id
                )
            )

            label = Label(
                text=category["name"],
                font_size=16,
                color=(0.13, 0.09, 0.05, 1),
                halign="left"
            )

            row.add_widget(checkbox)
            row.add_widget(label)

            self.categories_box.add_widget(row)

    # Загрузка ингредиентов
    def ingredients_loaded(self, request, data):

        self.ingredients_box.clear_widgets()

        grouped = {}

        # Группируем ингредиенты по типам
        for ingredient in data:

            ingredient_type = ingredient["type_name"]

            if ingredient_type not in grouped:
                grouped[ingredient_type] = []

            grouped[ingredient_type].append(ingredient)

        # Создаём группы ингредиентов
        for ingredient_type, ingredients in grouped.items():

            type_label = Label(
                text=ingredient_type,
                font_size=18,
                bold=True,
                color=(0.13, 0.09, 0.05, 1),
                size_hint_y=None,
                height=38,
                halign="left"
            )

            self.ingredients_box.add_widget(type_label)

            for ingredient in ingredients:

                row = BoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=42,
                    spacing=12
                )

                checkbox = ToggleButton(
                    text="",
                    size_hint=(None, None),
                    size=(28, 28)
                )

                style_toggle(checkbox)

                checkbox.bind(
                    state=lambda instance, value,
                    item_id=ingredient["id"]:
                    self.update_filter_toggle(
                        instance,
                        value,
                        self.selected_ingredient_ids,
                        item_id
                    )
                )

                label = Label(
                    text=ingredient["name"],
                    font_size=16,
                    color=(0.13, 0.09, 0.05, 1),
                    halign="left"
                )

                row.add_widget(checkbox)
                row.add_widget(label)

                self.ingredients_box.add_widget(row)

    # Поиск по выбранным фильтрам
    def search_recipes(self):

        params = []

        for category_id in sorted(self.selected_category_ids):

            params.append(
                ("category_ids", category_id)
            )

        for ingredient_id in sorted(self.selected_ingredient_ids):

            params.append(
                ("ingredient_ids", ingredient_id)
            )

        query_string = urlencode(params)

        url = "http://127.0.0.1:8000/search"

        if query_string:
            url += "?" + query_string

        UrlRequest(
            url,
            on_success=self.search_results_loaded,
            on_error=self.request_error,
            on_failure=self.request_error
        )

    # Отображение результатов расширенного поиска
    def search_results_loaded(self, request, data):

        self.search_results_layout.clear_widgets()

        if not data:

            self.search_results_layout.add_widget(
                Label(
                    text="Рецепты не найдены",
                    color=(0.13, 0.09, 0.05, 1),
                    size_hint_y=None,
                    height=50
                )
            )

            return

        for recipe in data:

            card = self.create_recipe_card(recipe)

            self.search_results_layout.add_widget(card)

    # Поиск по названию
    def search_by_name(self, query):

        query = query.strip()

        # Если поле пустое, показываем весь каталог
        if not query:

            UrlRequest(
                "http://127.0.0.1:8000/recipes",
                on_success=self.recipes_loaded,
                on_error=self.request_error,
                on_failure=self.request_error
            )

            return

        params = urlencode({"q": query})

        UrlRequest(
            f"http://127.0.0.1:8000/search?{params}",
            on_success=self.name_search_loaded,
            on_error=self.request_error,
            on_failure=self.request_error
        )

    # Отображение результатов поиска по названию
    def name_search_loaded(self, request, data):

        self.recipes_layout.clear_widgets()

        if not data:

            self.recipes_layout.add_widget(
                Label(
                    text="Рецепты не найдены",
                    color=(0.13, 0.09, 0.05, 1),
                    size_hint_y=None,
                    height=60
                )
            )

            return

        for recipe in data:

            card = self.create_recipe_card(recipe)

            self.recipes_layout.add_widget(card)

    # Загрузка всех рецептов
    def recipes_loaded(self, request, data):

        print("Рецепты успешно загружены!")

        self.recipes = data

        self.recipes_layout.clear_widgets()

        for recipe in self.recipes:

            card = self.create_recipe_card(recipe)

            self.recipes_layout.add_widget(card)

    # Обработка ошибок запросов
    def request_error(self, request, error):

        print("Ошибка загрузки рецептов:")
        print(error)

    # Создание приложения
    def build(self):

        # Хранилище избранных рецептов
        self.favorites_store = JsonStore("favorites.json")

        self.recipes = []

        # Менеджер экранов
        self.screen_manager = ScreenManager()

        self.main_screen = MainScreen(name="main")

        self.recipe_screen = RecipeScreen(name="recipe")

        self.favorite_screen = FavoriteScreen(name="favorites")

        self.search_screen = SearchScreen(name="search")

        self.screen_manager.add_widget(self.main_screen)
        self.screen_manager.add_widget(self.recipe_screen)
        self.screen_manager.add_widget(self.favorite_screen)
        self.screen_manager.add_widget(self.search_screen)

        # Главный макет
        main_layout = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        # Верхний контейнер
        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=120,
            padding=12,
            spacing=10
        )

        create_container(
            header,
            (0.79, 0.60, 0.29, 1)
        )

        # Заголовок
        title = Label(
            text="Каталог рецептов",
            font_size=26,
            size_hint_y=None,
            height=45
        )

        # Строка поиска
        search_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=40,
            spacing=5
        )

        # Поле ввода
        self.search_input = TextInput(
            hint_text="Найти рецепт...",
            size_hint_x=0.75,
            multiline=False,
            font_size=16,
            foreground_color=(0.13, 0.09, 0.05, 1),
            cursor_color=(0.13, 0.09, 0.05, 1),
            background_normal="",
            background_active="",
            background_color=(1, 1, 1, 1),
            padding=[10, 10]
        )

        self.search_input.bind(
            on_focus=lambda instance, value:
            print("Поле поиска получило фокус:", value)
        )

        # Поиск нажатием Enter
        self.search_input.bind(
            on_text_validate=lambda instance:
            self.search_by_name(instance.text)
        )

        # Кнопка поиска
        name_search_button = Button(
            text="Поиск",
            size_hint_x=0.25,
            font_size=14
        )

        style_button(
            name_search_button,
            color=(0.49, 0.34, 0.13, 1)
        )

        name_search_button.bind(
            on_release=lambda instance:
            self.search_by_name(self.search_input.text)
        )

        search_row.add_widget(self.search_input)
        search_row.add_widget(name_search_button)

        header.add_widget(title)
        header.add_widget(search_row)

        main_layout.add_widget(header)

        # Область со списком рецептов
        scroll = ScrollView(
            do_scroll_x=False
        )

        # Сетка карточек — две карточки в ряд
        self.recipes_layout = GridLayout(
            cols=2,
            spacing=12,
            size_hint_x=1,
            size_hint_y=None,
            padding=5
        )

        self.recipes_layout.bind(
            minimum_height=self.recipes_layout.setter("height")
        )

        scroll.add_widget(self.recipes_layout)

        main_layout.add_widget(scroll)

        # Нижняя панель навигации
        navigation = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=65,
            padding=8,
            spacing=5
        )

        create_container(
            navigation,
            (0.79, 0.60, 0.29, 1)
        )

        # Кнопка «Все рецепты»
        all_recipes_button = Button(
            text="Все рецепты",
            font_size=13
        )

        style_button(all_recipes_button)

        all_recipes_button.bind(
            on_release=lambda instance:
            self.show_all_recipes()
        )

        # Кнопка «Поиск»
        search_button = Button(
            text="Поиск",
            font_size=13
        )

        style_button(search_button)

        search_button.bind(
            on_release=lambda instance:
            self.show_search()
        )

        # Кнопка «Избранное»
        favorites_button = Button(
            text="Избранное",
            font_size=13
        )

        style_button(favorites_button)

        favorites_button.bind(
            on_release=lambda instance:
            self.show_favorites()
        )

        navigation.add_widget(all_recipes_button)
        navigation.add_widget(search_button)
        navigation.add_widget(favorites_button)

        main_layout.add_widget(navigation)

        self.main_screen.add_widget(main_layout)

        return self.screen_manager

    # Возврат ко всем рецептам
    def show_all_recipes(self):

        self.screen_manager.current = "main"

        # Снова загружаем полный каталог
        UrlRequest(
            "http://127.0.0.1:8000/recipes",
            on_success=self.recipes_loaded,
            on_error=self.request_error,
            on_failure=self.request_error
        )


if __name__ == "__main__":
    RecipeApp().run()