from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen   

from buttonImage import ButtonImage
from utils import Utils
from imageScreen import ImageScreen
 
class CollectionScreen(Screen):
    def __init__(self, collection, sm, cursor, **kwargs):
        super(CollectionScreen,self).__init__(**kwargs)
        self.collection = collection
        
        main_layout = BoxLayout(orientation = 'vertical')
        
        first_row = BoxLayout(orientation = 'horizontal',
                              size_hint = (1, .1))
        
        back_button = Button(text = 'Back')
        back_button.bind(on_press= lambda instance, sm=sm: self.go_main(sm=sm))
        
        collection_label = Label(text = collection)
        
        first_row.add_widget(back_button)
        first_row.add_widget(collection_label)
        
        main_layout.add_widget(first_row)
        
        imgs_grid = GridLayout(cols=4)
        
        collection_img_query = "select name, image from media_files where collection_id = (select collection_id from collections where name = %s)"
        
        img_list = cursor.exec_query(collection_img_query, (collection,))
        
        for name, bytea in img_list:
            Utils.bytea_to_image(bytea.tobytes(), f'media/{name}')
            
            Utils.decompress_image(f'media/{name}', f'media/{name}')
            
            img_preview = ButtonImage(source=f'media/{name}', size_hint_y=1)
            
            img_preview.bind(on_press = lambda istance, sm=sm, img_path=f'media/{name}', col=collection: self.open_img(sm=sm, img_path=img_path, collection=col, cursor=cursor))   
            
            imgs_grid.add_widget(img_preview)             

        main_layout.add_widget(imgs_grid)
        
        self.add_widget(main_layout)
        
    def go_main(self,sm):
        sm.current = 'main'
        
    def open_img(self,sm,img_path,collection, cursor):
        image_screen = ImageScreen(img_path=img_path,sm=sm, name=img_path, collection=collection, cursor=cursor)
        
        sm.add_widget(image_screen)
        
        sm.current = img_path