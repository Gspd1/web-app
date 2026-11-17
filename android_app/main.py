
from kivy.app import App
from kivy.uix.label import Label


class RecipeApp(App):

    def build(self):
        return Label(
            text="Мой каталог рецептов!",
            font_size=30
        )


if __name__ == "__main__":
    RecipeApp().run()
