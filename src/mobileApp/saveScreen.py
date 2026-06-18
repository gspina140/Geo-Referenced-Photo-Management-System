from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.image import Image
from datetime import datetime

from utils import Utils

class SaveScreen(Screen):
    def __init__(self, image, cursor, sm, collection=None,  **kwargs):
        super(SaveScreen, self).__init__(**kwargs)
        
        mainLayout = BoxLayout(orientation='vertical')
        
        backButton = Button(text='Undo', size_hint_y=.1)
        
        imgPreview = Image(source=f'media/{image}', size_hint_y=.5)
        
        self.inputName = TextInput(text='Insert image name',size_hint_y=.1)
        
        locationLabel = Label(text=f'Current position is: {Utils.get_location()}', size_hint_y=.1)
        
        saveButton = Button(text='Save image', size_hint_y=.1)
        
        saveButton.bind(on_press=lambda instance: self.save(image, cursor, sm))
        
        mainLayout.add_widget(backButton)
        mainLayout.add_widget(imgPreview)
        mainLayout.add_widget(self.inputName)
        
        self.collectionName = None
        
        if collection is not None:
            self.collection = collection
            collectionName = cursor.exec_query("select name from collections where collection_id = %s", (collection,))
            collectionLabel = Label(text=f'Saving in collection: {collectionName}',size_hint_y=.1)
            mainLayout.add_widget(collectionLabel)    
            backButton.bind(on_press=lambda instance: self.backCamera(sm))
        else:
            self.collectionName = TextInput(text='Insert collection name', size_hint_y=.1)
            mainLayout.add_widget(self.collectionName)
            backButton.bind(on_press=lambda instance: self.backMain(sm))
            
        mainLayout.add_widget(locationLabel)
        mainLayout.add_widget(saveButton)
        
        self.add_widget(mainLayout)
        
    def backCamera(self, sm):
        sm.current='camera0'
    
    def backMain(self, sm):
        sm.current='main'
        
    def save(self, img, cursor, sm):
        
        Utils.compress_image(f'media/{img}', f'media/{img}')
        
        bytea = Utils.image_to_bytea(f'media/{img}')
        
        if self.collectionName is not None:
            collectionName = self.collectionName.text
            collectionId = cursor.exec_query("select collection_id from collections c where name = %s", (collectionName,))[0]
        else:
            collectionId = self.collection
            
        saveImageQuery = "INSERT INTO media_files (collection_id, name, image, position, date) VALUES (%s, %s, %s, ST_GeogFromText('POINT(%s %s)'), %s) returning name;"
        
        latlng = Utils.get_coordinates() 
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.exec_insert_query(saveImageQuery,(collectionId, self.inputName.text+".png", bytea, latlng[1], latlng[0], date,))
        
        self.backMain(sm)
        