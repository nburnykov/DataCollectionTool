from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image

class AddLocationForm(BoxLayout):
    def search_location(self):
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>")

class FirstApp(App):
    pass

if __name__ == '__main__':
    FirstApp().run()