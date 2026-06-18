from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from utils import Utils
from buttonImage import ButtonImage
from imageScreen import ImageScreen


class NearestScreen(Screen):
    def __init__(self, sm, cursor, k, **kwargs):
        super(NearestScreen, self).__init__(**kwargs)

        main_layout = BoxLayout(orientation='vertical')

        first_row = BoxLayout(orientation='horizontal',
                              size_hint=(1, .1))

        back_button = Button(text='Back')
        back_button.bind(on_press=lambda instance, sm=sm: self.go_main(sm=sm))

        title_label = Label(
            text=f'The {k} photos taken nearest to your position')

        first_row.add_widget(back_button)
        first_row.add_widget(title_label)

        main_layout.add_widget(first_row)

        imgs_grid = GridLayout(cols=4)

        nearest_photos_query = """SELECT
                                    mf.name,
                                    mf.image,
                                    c.name,
                                    ST_Distance(mf.position::geography, 'POINT(%s %s)'::geography) AS distance
                                FROM
                                    media_files mf
                                JOIN
                                    collections c ON mf.collection_id = c.collection_id 
                                ORDER BY
                                    distance
                                LIMIT
                                    %s;"""

        latlng = Utils.get_coordinates()
        
        img_list = cursor.exec_query(nearest_photos_query, (latlng[1], latlng[0], k))

        for name, bytea, collection, distance in img_list:
            Utils.bytea_to_image(bytea.tobytes(), f'media/{name}')

            Utils.decompress_image(f'media/{name}', f'media/{name}')

            img_preview = ButtonImage(source=f'media/{name}', size_hint_y=1)

            img_preview.bind(on_press=lambda istance, sm=sm, img_path=f'media/{name}', col=collection: self.open_img(
                sm=sm, img_path=img_path, collection=col, cursor=cursor))

            imgs_grid.add_widget(img_preview)
            
        main_layout.add_widget(imgs_grid)
        
        self.add_widget(main_layout)

    def go_main(self, sm):
        sm.current = 'main'

    def open_img(self, sm, img_path, collection, cursor):
        image_screen = ImageScreen(
            img_path=img_path, sm=sm, name=img_path, collection=collection, cursor=cursor)

        sm.add_widget(image_screen)

        sm.current = img_path
