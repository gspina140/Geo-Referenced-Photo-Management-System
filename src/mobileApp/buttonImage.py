from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image

class ButtonImage(ButtonBehavior, Image):
    def __init__(self, source, size_hint_y=None, **kwargs):
        super(ButtonImage,self).__init__(**kwargs)
        self.source = source
        self.size_hint_y = size_hint_y