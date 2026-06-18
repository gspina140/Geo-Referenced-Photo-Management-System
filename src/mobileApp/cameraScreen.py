#from kivy.uix.camera import Camera
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image  
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2

from utils import Utils
from saveScreen import SaveScreen

class opencvCamera(Image):
    def __init__(self, capture, fps, **kwargs):
        super(opencvCamera, self).__init__(**kwargs)
        self.capture = capture
        Clock.schedule_interval(self.update, 1.0 / fps)
    
    def update(self, dt):
        succ, frame = self.capture.read()

        if succ:
            # convert it to texture
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from
            self.texture = image_texture
    
    def get_image(self):
        succ, frame = self.capture.read()
        
        if succ:
            return frame
        else:
            return None

class CameraScreen(Screen):
    def __init__(self, sm, cursor, collection=None, **kwargs):
        super(CameraScreen, self).__init__(**kwargs)
        
        mainLayout = BoxLayout(orientation='vertical')
        
        self.cap = cv2.VideoCapture(0)
        self.camera = opencvCamera(self.cap, 30)
        
        photoButton = Button(text="Take Photo", size_hint=(.5, .2), pos_hint={'x': .25, 'y': .75})
        
        photoButton.bind(on_press=lambda instance: self.acquire_image(sm, cursor=cursor, collection=collection))

        mainLayout.add_widget(self.camera)

        mainLayout.add_widget(photoButton)

        self.add_widget(mainLayout)

    def acquire_image(self, sm, cursor, collection):
        img = self.camera.get_image()
        
        cv2.imwrite('media/temp.png', img)
        
        saveScreen = SaveScreen(name='save',image='temp.png', cursor=cursor, collection=collection, sm=sm)
        sm.add_widget(saveScreen)
        
        sm.current= 'save'
