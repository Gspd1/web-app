from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.graphics import StencilPush, StencilUse, StencilUnUse, StencilPop
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.network.urlrequest import UrlRequest
from kivy.uix.image import AsyncImage

# Размер окна для разработки на компьютере
Window.size = (400, 700)

def create_container(layout, color):
    with layout.canvas.before:
        Color(*color)
        layout.background = RoundedRectangle(
            pos=layout.pos,
            size=layout.size,
            radius=[15]
        )

    layout.bind(
        pos=lambda instance, value: setattr(
            layout.background, "pos", value
        ),
        size=lambda instance, value: setattr(
            layout.background, "size", value
        )
    )

def style_button(button):
    with button.canvas.before:
        Color(0.79, 0.60, 0.29, 1)
        button.bg = RoundedRectangle(
            pos=button.pos,
            size=button.size,
            radius=[5]
        )

    button.bind(
        pos=lambda instance, value: setattr(button.bg, "pos", value),
        size=lambda instance, value: setattr(button.bg, "size", value)
    )

    button.background_color = (0, 0, 0, 0)
    button.background_normal = ""
    button.color = (0, 0, 0, 1)



class MainScreen(Screen):
    pass

class RecipeScreen(Screen):
    pass




class RecipeApp(App):
    def open_recipe(self, recipe_id):
        UrlRequest(
            f"http://127.0.0.1:8000/recipes/{recipe_id}",
            on_success=self.recipe_details_loaded,
            on_error=self.request_error,
            on_failure=self.request_error
        )

    def recipe_details_loaded(self, request, data):
        # Получаем данные рецепта
        recipe = data["recipe"]
        ingredients = data["ingredients"]

        # Очищаем предыдущую страницу
        self.recipe_screen.clear_widgets()

        # Создаём прокручиваемую область
        scroll = ScrollView()

        # Создаём макет для содержимого рецепта
        recipe_layout = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10,
            size_hint_y=None
        )

        # Высота макета будет зависеть от его содержимого
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
            on_press=lambda instance:
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

        # Заголовок ингредиентов
        ingredients_title = Label(
            text="Ингредиенты",
            font_size=20,
            color=(0.13, 0.09, 0.05, 1),
            size_hint_y=None,
            height=40
        )
        recipe_layout.add_widget(ingredients_title)

        # Выводим список ингредиентов
        for ingredient in ingredients:
            ingredient_label = Label(
                text=f'{ingredient["name"]} — {ingredient["amount"]} {ingredient["unit"]}',
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

        # Выводим каждый шаг приготовления
        for step in data["steps"]:

            # Номер и описание шага
            step_label = Label(
                text=f'{step["recipe_step_number"]}. {step["recipe_step_description"]}',
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

            # Если у шага есть фотография, показываем её
            if step["recipe_step_image"] is not None:
                step_image = AsyncImage(
                    source="http://127.0.0.1:8000/" + step["recipe_step_image"],
                    size_hint_y=None,
                    height=160,
                    allow_stretch=True,
                    keep_ratio=False
                )

                recipe_layout.add_widget(step_image)

        # Добавляем содержимое в прокручиваемую область
        scroll.add_widget(recipe_layout)

        # Добавляем прокрутку на экран рецепта
        self.recipe_screen.add_widget(scroll)

        # Открываем страницу рецепта
        self.screen_manager.current = "recipe"

    def on_start(self):
        # Отправляем запрос к FastAPI
        UrlRequest(
            "http://127.0.0.1:8000/recipes",
            on_success=self.recipes_loaded,
            on_error=self.request_error,
            on_failure=self.request_error
        )



    def on_start(self):
        # Отправляем запрос к FastAPI
        UrlRequest(
            "http://127.0.0.1:8000/recipes",
            on_success=self.recipes_loaded,
            on_error=self.request_error,
            on_failure=self.request_error
        )

    def recipes_loaded(self, request, data):
        print("Рецепты успешно загружены!")

        # Сохраняем полученные рецепты
        self.recipes = data

        # Очищаем список карточек
        self.recipes_layout.clear_widgets()

        # Создаём карточки из данных базы
        for recipe in self.recipes:

            card = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=200,
                padding=10,
                spacing=5
            )

            create_container(card, (0.49, 0.34, 0.13, 1))

            # Загружаем фотографию с сервера
            recipe_image = AsyncImage(
                source="http://127.0.0.1:8000/" + recipe["image_path"],
                size_hint=(1, 0.8),
                allow_stretch=True,
                keep_ratio=False
            )

            # Название рецепта
            recipe_name = Label(
                text=recipe["name"],
                font_size=16,
                color=(0.13, 0.09, 0.05, 1),
                size_hint=(1, 0.2)
            )

            card.add_widget(recipe_image)
            card.add_widget(recipe_name)

            # Переход на страницу рецепта
            card.bind(
                on_touch_down=lambda instance, touch, recipe_id=recipe["id"]:
                self.open_recipe(recipe_id)
                if instance.collide_point(*touch.pos)
                else None
            )

            self.recipes_layout.add_widget(card)

    def request_error(self, request, error):
        print("Ошибка загрузки рецептов:")
        print(error)



    def build(self):
        # Создаём менеджер экранов
        self.screen_manager = ScreenManager()

        # Создаём главный экран
        self.main_screen = MainScreen(name="main")

        # Создаём экран отдельного рецепта
        self.recipe_screen = RecipeScreen(name="recipe")

        # Добавляем экраны в менеджер
        self.screen_manager.add_widget(self.main_screen)
        self.screen_manager.add_widget(self.recipe_screen)


        # Главный макет
        main_layout = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        # Верхняя часть экрана
        # Верхний контейнер
        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=120,
            padding=12,
            spacing=10
        )

        create_container(header, (0.79, 0.60, 0.29, 1))

        # Название приложения
        title = Label(
            text="Каталог рецептов",
            font_size=26,
            size_hint_y=None,
            height=50
        )

        # Поле поиска
        search = TextInput(
            hint_text="Найти рецепт...",
            size_hint_y=None,
            height=45,
            multiline=False
        )

        with search.canvas.before:
            Color(1, 1, 1, 1)
            search.bg = RoundedRectangle(
                pos=search.pos,
                size=search.size,
                radius=[8]
            )

        search.bind(
            pos=lambda instance, value: setattr(search.bg, "pos", value),
            size=lambda instance, value: setattr(search.bg, "size", value)
        )

        search.background_color = (0, 0, 0, 0)
        search.background_normal = ""
        search.background_active = ""
        search.foreground_color = (0.13, 0.09, 0.05, 1)
        search.cursor_color = (0.13, 0.09, 0.05, 1)


        # Добавляем заголовок и поиск в шапку
        header.add_widget(title)
        header.add_widget(search)

        # Добавляем шапку на главный экран
        main_layout.add_widget(header)

        # Область со списком рецептов
        scroll = ScrollView()

        # Макет для карточек рецептов
        # Макет для карточек рецептов
        self.recipes_layout = GridLayout(
            cols=2,
            spacing=15,
            size_hint_y=None,
            padding=5
        )

        self.recipes_layout.bind(
            minimum_height=self.recipes_layout.setter("height")
        )


        # Добавляем список в прокручиваемую область
        scroll.add_widget(self.recipes_layout)
        main_layout.add_widget(scroll)

        # Цвет фона приложения
        Window.clearcolor = (0.89, 0.86, 0.83, 1)



        # Нижняя панель навигации
        # Нижний контейнер
        navigation = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=65,
            padding=8,
            spacing=5
        )

        create_container(navigation, (0.79, 0.60, 0.29, 1))



        # Кнопка "Все рецепты"
        all_recipes_button = Button(
            text="Все рецепты",
            font_size=14
        )

        # Кнопка "Поиск"
        search_button = Button(
            text="Поиск",
            font_size=14
        )

        # Кнопка "Избранное"
        favorites_button = Button(
            text="Избранное",
            font_size=14
        )

        # Добавляем кнопки на панель
        navigation.add_widget(all_recipes_button)
        navigation.add_widget(search_button)
        navigation.add_widget(favorites_button)
        style_button(all_recipes_button)
        style_button(search_button)
        style_button(favorites_button)

        # Добавляем панель на главный экран
        main_layout.add_widget(navigation)

        self.main_screen.add_widget(main_layout)

        return self.screen_manager


if __name__ == "__main__":
    RecipeApp().run()
