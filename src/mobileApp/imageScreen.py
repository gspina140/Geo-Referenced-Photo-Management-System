from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from pathlib import Path

class ImageScreen(Screen):
    def __init__(self, img_path, sm, collection, cursor, **kwargs):
        super(ImageScreen, self).__init__(**kwargs)
        name = Path(img_path).name
        
        main_layout = BoxLayout(orientation = 'vertical')
        
        first_row = BoxLayout(orientation = 'horizontal',
                              size_hint = (1, .1))
    
        back_button = Button(text = 'Back to collection')
                                      
        back_button.bind(on_press= lambda instance, sm=sm,col = collection: self.go_reference_collection(sm=sm,collection=col))

        delete_button = Button(text = 'Delete')
        delete_button.bind(on_press= lambda instance: self.delete_photo(sm, collection, name, cursor))
        
        first_row.add_widget(back_button)
        first_row.add_widget(delete_button)
        
        main_layout.add_widget(first_row)
        
        img = Image(source=img_path)
        
        main_layout.add_widget(img)
        
        self.add_widget(main_layout)
        
    def go_reference_collection(self, sm, collection):
        sm.current = collection
        
    def delete_photo(self, sm, collection, img, cursor):
        
        delete_query = "delete from media_files where name= %s returning collection_id;"
        
        cursor.exec_insert_query(delete_query, (img,))
        
        sm.current = collection
        
        