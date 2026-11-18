from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.graphics import StencilPush, StencilUse, StencilUnUse, StencilPop
from kivy.network.urlrequest import UrlRequest
from kivy.storage.jsonstore import JsonStore
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from urllib.parse import urlencode


# Размер окна для разработки на компьютере
Window.size = (400, 700)

# Общие цвета приложения
BG_COLOR = (0.89, 0.86, 0.83, 1)
LIGHT_BROWN = (0.79, 0.60, 0.29, 1)
DARK_BROWN = (0.49, 0.34, 0.13, 1)
TEXT_COLOR = (0.13, 0.09, 0.05, 1)
WHITE = (1, 1, 1, 1)

# Пока приложение запускается на компьютере.
# Для Android-эмулятора позже заменим адрес на http://10.0.2.2:8000
API_URL = "http://127.0.0.1:8000"


def create_container(layout, color):
    """Рисует контейнер со скруглёнными углами."""
    with layout.canvas.before:
        Color(*color)
        layout.background = RoundedRectangle(
            pos=layout.pos,
            size=layout.size,
            radius=[15]
        )

    layout.bind(
        pos=lambda instance, value: setattr(layout.background, "pos", value),
        size=lambda instance, value: setattr(layout.background, "size", value)
    )


def style_button(button, color=LIGHT_BROWN, radius=12):
    """Оформляет кнопку со скруглёнными углами."""
    with button.canvas.before:
        Color(*color)
        button.bg = RoundedRectangle(
            pos=button.pos,
            size=button.size,
            radius=[radius]
        )

    button.bind(
        pos=lambda instance, value: setattr(button.bg, "pos", value),
        size=lambda instance, value: setattr(button.bg, "size", value)
    )

    button.background_color = (0, 0, 0, 0)
    button.background_normal = ""
    button.background_down = ""
    button.color = TEXT_COLOR


class RoundedAsyncImage(AsyncImage):
    """Изображение, обрезанное по скруглённой форме."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            StencilPush()
            self.clip_before = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[12]
            )
            StencilUse()

        with self.canvas.after:
            StencilUnUse()
            self.clip_after = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[12]
            )
            StencilPop()

        self.bind(
            pos=self.update_clip,
            size=self.update_clip
        )

    def update_clip(self, *args):
        self.clip_before.pos = self.pos
        self.clip_before.size = self.size
        self.clip_after.pos = self.pos
        self.clip_after.size = self.size


class MainScreen(Screen):
    pass


class RecipeScreen(Screen):
    pass


class FavoriteScreen(Screen):
    pass


class SearchScreen(Screen):
    pass


class RecipeApp(App):

    # ---------------------------------------------------------
    # Общие функции
    # ---------------------------------------------------------

    def request_error(self, request, error):
        print("Ошибка запроса к серверу:")
        print(error)

    def load_recipes(self):
        """Загружает весь каталог рецептов."""
        UrlRequest(
            f"{API_URL}/recipes",
            on_success=self.recipes_loaded,
            on_error=self.request_error,
            on_failure=self.request_error
        )

    def create_recipe_card(self, recipe, target_layout):
        """Создаёт одну карточку рецепта и добавляет её в сетку."""
        card = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=200,
            padding=8,
            spacing=5
        )
        create_container(card, DARK_BROWN)

        recipe_image = RoundedAsyncImage(
            source=f"{API_URL}/{recipe['image_path']}",
            size_hint=(1, 0.78),
            allow_stretch=True,
            keep_ratio=False
        )

        recipe_name = Label(
            text=recipe["name"],
            font_size=15,
            color=WHITE,
            size_hint=(1, 0.22),
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
            on_touch_down=lambda instance, touch, recipe_id=recipe["id"]:
            self.open_recipe(recipe_id)
            if instance.collide_point(*touch.pos)
            else None
        )

        target_layout.add_widget(card)

    def create_recipe_grid(self):
        """Создаёт сетку карточек в две колонки."""
        grid = GridLayout(
            cols=2,
            spacing=10,
            padding=5,
            size_hint=(1, None),
            col_force_default=False
        )
        grid.bind(minimum_height=grid.setter("height"))
        return grid

    # ---------------------------------------------------------
    # Главный экран и каталог
    # ---------------------------------------------------------

    def recipes_loaded(self, request, data):
        print("Рецепты успешно загружены!")

        self.recipes = data
        self.recipes_layout.clear_widgets()

        for recipe in self.recipes:
            self.create_recipe_card(recipe, self.recipes_layout)

    def search_by_name(self, query):
        query = query.strip()

        if not query:
            self.load_recipes()
            return

        params = urlencode({"q": query})

        UrlRequest(
            f"{API_URL}/search?{params}",
            on_success=self.name_search_loaded,
            on_error=self.request_error,
            on_failure=self.request_error
        )

    def name_search_loaded(self, request, data):
        self.recipes_layout.clear_widgets()

        if not data:
            self.recipes_layout.add_widget(
                Label(
                    text="Рецепты не найдены",
                    color=TEXT_COLOR,
                    size_hint_y=None,
                    height=60
                )
            )
            return

        for recipe in data:
            self.create_recipe_card(recipe, self.recipes_layout)

    # ---------------------------------------------------------
    # Страница отдельного рецепта
    # ---------------------------------------------------------

    def open_recipe(self, recipe_id):
        UrlRequest(
            f"{API_URL}/recipes/{recipe_id}",
            on_success=self.recipe_details_loaded,
            on_error=self.request_error,
            on_failure=self.request_error
        )

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

        title = Label(
            text=recipe["name"],
            font_size=24,
            color=TEXT_COLOR,
            size_hint_y=None,
            height=55,
            halign="center",
            valign="middle"
        )
        title.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", value)
        )
        recipe_layout.add_widget(title)

        recipe_image = RoundedAsyncImage(
            source=f"{API_URL}/{recipe['image_path']}",
            size_hint_y=None,
            height=200,
            allow_stretch=True,
            keep_ratio=False
        )
        recipe_layout.add_widget(recipe_image)

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

        ingredients_title = Label(
            text="Ингредиенты",
            font_size=20,
            bold=True,
            color=TEXT_COLOR,
            size_hint_y=None,
            height=40
        )
        recipe_layout.add_widget(ingredients_title)

        for ingredient in ingredients:
            ingredient_label = Label(
                text=f'{ingredient["name"]} — {ingredient["amount"]} {ingredient["unit"]}',
                font_size=16,
                color=TEXT_COLOR,
                size_hint_y=None,
                height=30
            )
            recipe_layout.add_widget(ingredient_label)

        steps_title = Label(
            text="Приготовление",
            font_size=20,
            bold=True,
            color=TEXT_COLOR,
            size_hint_y=None,
            height=45
        )
        recipe_layout.add_widget(steps_title)

        for step in data["steps"]:
            step_label = Label(
                text=f'{step["recipe_step_number"]}. {step["recipe_step_description"]}',
                font_size=16,
                color=TEXT_COLOR,
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

            if step["recipe_step_image"] is not None:
                step_image = RoundedAsyncImage(
                    source=f"{API_URL}/{step['recipe_step_image']}",
                    size_hint_y=None,
                    height=160,
                    allow_stretch=True,
                    keep_ratio=False
                )
                recipe_layout.add_widget(step_image)

        scroll.add_widget(recipe_layout)
        self.recipe_screen.add_widget(scroll)
        self.screen_manager.current = "recipe"

    # ---------------------------------------------------------
    # Избранное
    # ---------------------------------------------------------

    def toggle_favorite(self, recipe_id, button):
        key = str(recipe_id)

        if self.favorites_store.exists(key):
            self.favorites_store.delete(key)
            button.text = "Добавить в избранное"
            print("Рецепт удалён из избранного")
        else:
            self.favorites_store.put(key, recipe_id=recipe_id)
            button.text = "Удалить из избранного"
            print("Рецепт добавлен в избранное")

    def show_favorites(self):
        self.favorite_screen.clear_widgets()

        layout = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        title = Label(
            text="Избранное",
            font_size=24,
            color=TEXT_COLOR,
            size_hint_y=None,
            height=50
        )
        layout.add_widget(title)

        back_button = Button(
            text="Все рецепты",
            size_hint_y=None,
            height=45
        )
        style_button(back_button)
        back_button.bind(
            on_release=lambda instance:
            self.show_all_recipes()
        )
        layout.add_widget(back_button)

        scroll = ScrollView()
        recipes_layout = self.create_recipe_grid()

        favorite_ids = [
            int(key) for key in self.favorites_store.keys()
        ]

        for recipe in self.recipes:
            if recipe["id"] in favorite_ids:
                self.create_recipe_card(recipe, recipes_layout)

        if not favorite_ids:
            recipes_layout.add_widget(
                Label(
                    text="В избранном пока пусто",
                    color=TEXT_COLOR,
                    size_hint_y=None,
                    height=60
                )
            )

        scroll.add_widget(recipes_layout)
        layout.add_widget(scroll)

        self.favorite_screen.add_widget(layout)
        self.screen_manager.current = "favorites"

    # ---------------------------------------------------------
    # Расширенный поиск
    # ---------------------------------------------------------

    def show_search(self):
        self.selected_category_ids = set()
        self.selected_ingredient_ids = set()

        self.search_screen.clear_widgets()

        scroll = ScrollView()

        content = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=12,
            size_hint_y=None
        )
        content.bind(
            minimum_height=content.setter("height")
        )

        title = Label(
            text="Расширенный поиск",
            font_size=24,
            bold=True,
            color=TEXT_COLOR,
            size_hint_y=None,
            height=55
        )
        content.add_widget(title)

        back_button = Button(
            text="Все рецепты",
            size_hint_y=None,
            height=45
        )
        style_button(back_button)
        back_button.bind(
            on_release=lambda instance:
            self.show_all_recipes()
        )
        content.add_widget(back_button)

        form_box = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10,
            size_hint_y=None
        )
        form_box.bind(
            minimum_height=form_box.setter("height")
        )
        create_container(form_box, LIGHT_BROWN)

        categories_title = Label(
            text="Категории",
            font_size=23,
            bold=True,
            color=TEXT_COLOR,
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

        ingredients_title = Label(
            text="Ингредиенты",
            font_size=23,
            bold=True,
            color=TEXT_COLOR,
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

        find_button = Button(
            text="Найти рецепты",
            size_hint_y=None,
            height=50,
            font_size=17
        )
        style_button(find_button, DARK_BROWN)
        find_button.bind(
            on_release=lambda instance: self.search_recipes()
        )
        form_box.add_widget(find_button)

        content.add_widget(form_box)

        results_title = Label(
            text="Результаты поиска",
            font_size=21,
            bold=True,
            color=TEXT_COLOR,
            size_hint_y=None,
            height=50
        )
        content.add_widget(results_title)

        self.search_results_layout = self.create_recipe_grid()
        content.add_widget(self.search_results_layout)

        scroll.add_widget(content)
        self.search_screen.add_widget(scroll)
        self.screen_manager.current = "search"

        UrlRequest(
            f"{API_URL}/recipe-types",
            on_success=self.categories_loaded,
            on_error=self.request_error,
            on_failure=self.request_error
        )

        UrlRequest(
            f"{API_URL}/ingredients",
            on_success=self.ingredients_loaded,
            on_error=self.request_error,
            on_failure=self.request_error
        )

    def update_selection(self, selected_ids, item_id, active):
        if active:
            selected_ids.add(item_id)
        else:
            selected_ids.discard(item_id)

    def update_filter_toggle(self, button, state, selected_ids, item_id):
        self.update_selection(
            selected_ids,
            item_id,
            state == "down"
        )

        if state == "down":
            button.text = "✓"
            button.background_color = DARK_BROWN
            button.color = WHITE
        else:
            button.text = ""
            button.background_color = BG_COLOR
            button.color = TEXT_COLOR

    def create_filter_checkbox(self, item_id, selected_ids):
        checkbox = ToggleButton(
            text="",
            size_hint=(None, None),
            size=(28, 28),
            background_normal="",
            background_down="",
            background_color=BG_COLOR,
            color=TEXT_COLOR
        )

        # Скруглённая подложка переключателя
        with checkbox.canvas.before:
            Color(*BG_COLOR)
            checkbox.rounded_bg = RoundedRectangle(
                pos=checkbox.pos,
                size=checkbox.size,
                radius=[6]
            )
        checkbox.bind(
            pos=lambda instance, value:
            setattr(checkbox.rounded_bg, "pos", value),
            size=lambda instance, value:
            setattr(checkbox.rounded_bg, "size", value)
        )

        checkbox.bind(
            state=lambda instance, value:
            self.update_filter_toggle(
                instance,
                value,
                selected_ids,
                item_id
            )
        )
        return checkbox

    def categories_loaded(self, request, data):
        self.categories_box.clear_widgets()

        for category in data:
            row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=42,
                spacing=12
            )

            checkbox = self.create_filter_checkbox(
                category["id"],
                self.selected_category_ids
            )

            label = Label(
                text=category["name"],
                font_size=16,
                color=TEXT_COLOR,
                halign="left"
            )

            row.add_widget(checkbox)
            row.add_widget(label)
            self.categories_box.add_widget(row)

    def ingredients_loaded(self, request, data):
        self.ingredients_box.clear_widgets()

        grouped = {}

        for ingredient in data:
            ingredient_type = ingredient["type_name"]

            if ingredient_type not in grouped:
                grouped[ingredient_type] = []

            grouped[ingredient_type].append(ingredient)

        for ingredient_type, ingredients in grouped.items():
            type_label = Label(
                text=ingredient_type,
                font_size=18,
                bold=True,
                color=TEXT_COLOR,
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

                checkbox = self.create_filter_checkbox(
                    ingredient["id"],
                    self.selected_ingredient_ids
                )

                label = Label(
                    text=ingredient["name"],
                    font_size=16,
                    color=TEXT_COLOR,
                    halign="left"
                )

                row.add_widget(checkbox)
                row.add_widget(label)
                self.ingredients_box.add_widget(row)

    def search_recipes(self):
        params = []

        for category_id in sorted(self.selected_category_ids):
            params.append(("category_ids", category_id))

        for ingredient_id in sorted(self.selected_ingredient_ids):
            params.append(("ingredient_ids", ingredient_id))

        query_string = urlencode(params)
        url = f"{API_URL}/search"

        if query_string:
            url += "?" + query_string

        UrlRequest(
            url,
            on_success=self.search_results_loaded,
            on_error=self.request_error,
            on_failure=self.request_error
        )

    def search_results_loaded(self, request, data):
        self.search_results_layout.clear_widgets()

        if not data:
            self.search_results_layout.add_widget(
                Label(
                    text="Рецепты не найдены",
                    color=TEXT_COLOR,
                    size_hint_y=None,
                    height=50
                )
            )
            return

        for recipe in data:
            self.create_recipe_card(recipe, self.search_results_layout)

    # ---------------------------------------------------------
    # Переключение на главный экран
    # ---------------------------------------------------------

    def show_all_recipes(self):
        self.screen_manager.current = "main"
        self.load_recipes()

    # ---------------------------------------------------------
    # Создание интерфейса
    # ---------------------------------------------------------

    def build(self):
        self.favorites_store = JsonStore("favorites.json")
        self.recipes = []

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

        # Верхняя панель — высота возвращена к 120
        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=120,
            padding=10,
            spacing=5
        )
        create_container(header, LIGHT_BROWN)

        title = Label(
            text="Каталог рецептов",
            font_size=26,
            size_hint_y=None,
            height=50,
            color=TEXT_COLOR
        )
        header.add_widget(title)

        search_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=40,
            spacing=5
        )

        self.search_input = TextInput(
            hint_text="Найти рецепт...",
            size_hint_x=0.75,
            multiline=False,
            font_size=16,
            foreground_color=TEXT_COLOR,
            cursor_color=TEXT_COLOR,
            background_normal="",
            background_active="",
            background_color=(0, 0, 0, 0),
            padding=[10, 10]
        )

        # Белый фон поля поиска со скруглёнными углами
        with self.search_input.canvas.before:
            Color(*WHITE)
            self.search_input.rounded_bg = RoundedRectangle(
                pos=self.search_input.pos,
                size=self.search_input.size,
                radius=[10]
            )

        self.search_input.bind(
            pos=lambda instance, value:
            setattr(self.search_input.rounded_bg, "pos", value),
            size=lambda instance, value:
            setattr(self.search_input.rounded_bg, "size", value)
        )

        self.search_input.bind(
            on_text_validate=lambda instance:
            self.search_by_name(instance.text)
        )

        name_search_button = Button(
            text="Поиск",
            size_hint_x=0.25,
            font_size=14
        )
        style_button(name_search_button, DARK_BROWN)
        name_search_button.bind(
            on_release=lambda instance:
            self.search_by_name(self.search_input.text)
        )

        search_row.add_widget(self.search_input)
        search_row.add_widget(name_search_button)
        header.add_widget(search_row)
        main_layout.add_widget(header)

        # Область со списком рецептов
        scroll = ScrollView()

        self.recipes_layout = self.create_recipe_grid()
        scroll.add_widget(self.recipes_layout)
        main_layout.add_widget(scroll)

        Window.clearcolor = BG_COLOR

        # Нижняя панель навигации
        navigation = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=65,
            padding=8,
            spacing=5
        )
        create_container(navigation, LIGHT_BROWN)

        all_recipes_button = Button(
            text="Все рецепты",
            font_size=14
        )
        search_button = Button(
            text="Поиск",
            font_size=14
        )
        favorites_button = Button(
            text="Избранное",
            font_size=14
        )

        style_button(all_recipes_button, DARK_BROWN)
        style_button(search_button, DARK_BROWN)
        style_button(favorites_button, DARK_BROWN)

        all_recipes_button.bind(
            on_release=lambda instance: self.show_all_recipes()
        )
        search_button.bind(
            on_release=lambda instance: self.show_search()
        )
        favorites_button.bind(
            on_release=lambda instance: self.show_favorites()
        )

        navigation.add_widget(all_recipes_button)
        navigation.add_widget(search_button)
        navigation.add_widget(favorites_button)

        main_layout.add_widget(navigation)
        self.main_screen.add_widget(main_layout)

        return self.screen_manager

    def on_start(self):
        self.load_recipes()


if __name__ == "__main__":
    RecipeApp().run()
