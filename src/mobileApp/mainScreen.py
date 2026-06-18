from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from datetime import datetime

from utils import Utils
from buttonImage import ButtonImage
from collectionScreen import CollectionScreen
from cameraScreen import CameraScreen
from nearestScreen import NearestScreen

class MainScreen(Screen):
    def __init__(self, sm, cursor, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
     
        main_layout = BoxLayout(orientation = 'vertical')
        
        first_row = BoxLayout(orientation = 'horizontal',
                              size_hint = (1, .1))

        popup_content = BoxLayout(orientation='vertical')
        
        input_name = TextInput(text='Insert Collection Name',
                               on_text_validate=lambda instance: self.on_enter(),
                               size_hint=(1, .7))
        
        submit_button = Button(text='Create Collection',
                               size_hint=(1, .3))
        
        popup_content.add_widget(input_name)
        
        popup_content.add_widget(submit_button)
        
        self.new_collection_popup = Popup(title='Create new collection',
                                    content = popup_content,
                                    size_hint=(.3,.3))
                              
        new_colletion_button = Button(text = 'Add Collection')
        
        new_colletion_button.bind(on_press= self.new_collection_popup.open)

        submit_button.bind(on_press=lambda instance: (self.new_collection_popup.dismiss(), self.create_new_collection(input_name.text,cursor, sm)))
                
        location = Utils.get_location()
        
        self.coordinates_label = Label(text = f'Location: {str(location)}')
        
        get_nearest_content = BoxLayout(orientation='vertical')
        
        input_parameter = TextInput(text='Insert the number of nearest photos to retrieve')
        
        submit_parameter = Button(text='Retrieve photos')
        
        get_nearest_content.add_widget(input_parameter)        
        
        get_nearest_content.add_widget(submit_parameter)
        
        self.get_nearest_popup = Popup(title='Retrieve the photos taken near to you',
                                  content=get_nearest_content,
                                  size_hint=(.3, .3))
        
        get_nearest_button = Button(text='Retrieve photos near to you')
        
        get_nearest_button.bind(on_press=self.get_nearest_popup.open)
        
        submit_parameter.bind(on_press=lambda instance: (self.get_nearest_popup.dismiss(), self.get_nearest(sm, cursor, input_parameter.text)))
                                 
        first_row.add_widget(new_colletion_button)
        first_row.add_widget(self.coordinates_label)
        first_row.add_widget(get_nearest_button)
        
        main_layout.add_widget(first_row)

        collection_list = GridLayout(cols = 3,
                                    size_hint = (1,.7))
        
        collections_query = "select name from collections"
        
        collections = cursor.exec_query(collections_query)
        
        for collection in collections:
            first_img_query = "select name, image from media_files where collection_id = (select collection_id from collections where name = %s) limit 1"
            
            name, bytea = cursor.exec_query(first_img_query, (collection[0],))[0]
            
            Utils.bytea_to_image(bytea.tobytes(), f'media/{name}')
            
            Utils.decompress_image(f'media/{name}', f'media/{name}')
            
            collection_preview = BoxLayout(orientation='vertical')
            
            coll_name = Label(text=collection[0], size_hint_y=.1)
            
            img_prev = ButtonImage(source=f'media/{name}', size_hint_y=.9)
            
            collection_screen = CollectionScreen(name=collection[0], collection=collection[0], sm = sm, cursor=cursor)
            
            sm.add_widget(collection_screen)
            
            img_prev.bind(on_press = lambda instance, col=collection[0], sm=sm: self.open_collection(collection= col, sm=sm) )
            
            collection_preview.add_widget(coll_name)
            
            collection_preview.add_widget(img_prev)
            
            collection_list.add_widget(collection_preview)
            
        main_layout.add_widget(collection_list)
        
        open_camera_button = Button(text = 'Camera',
                                    size_hint = (1,.2))
        
        open_camera_button.bind(on_press=lambda instance: self.open_camera(sm, cursor))
        
        main_layout.add_widget(open_camera_button)  
        
        self.add_widget(main_layout)
           
    def on_enter(self):
        self.new_collection_popup.dismiss
        
    
    def open_collection(self, collection, sm):
        sm.current = collection    
    
    def create_new_collection(self, collection_name, cursor, sm):
        #self.new_collection_popup.dismiss
        
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        create_collection_query= "insert  into collections (name, created_at) values (%s,%s) returning collection_id;"
        new_collection_id = cursor.exec_insert_query(create_collection_query, (collection_name,date,))[0]
        
        cameraScreen = CameraScreen(name='camera0', sm=sm , cursor=cursor, collection=new_collection_id)
        sm.add_widget(cameraScreen)
        sm.current='camera0'
        
        
    def open_camera(self, sm, cursor):      
          
        camera_screen = CameraScreen(name='camera',sm=sm, cursor=cursor)
        sm.add_widget(camera_screen)
        
        sm.current='camera'
        
    def get_nearest(self, sm, cursor, k):
        nearestScreen = NearestScreen(name='nearest', sm=sm, cursor=cursor, k=k)
        
        sm.add_widget(nearestScreen)
        
        sm.current= 'nearest'