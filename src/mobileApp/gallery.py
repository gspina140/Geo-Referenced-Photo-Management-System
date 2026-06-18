from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from mainScreen import MainScreen

import os

from dbHandler import DbHandler

src_dir = os.getcwd()

def back_home(sm):
    sm.current = 'main'
    
class Gallery(App):
    def __init__(self):
        super().__init__()

        self.dir = os.getcwd()

    def build(self):
        
        db = DbHandler()
        
        self.sm = ScreenManager()
        
        main_window = MainScreen(sm = self.sm, cursor=db, name='main')
        
        self.sm.add_widget(main_window)
        
        self.sm.current = 'main'
        
        return self.sm
    
            
if __name__ == '__main__':
    app = Gallery()
    app.run()
