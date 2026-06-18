from flask import Flask, request, jsonify, render_template
from dbHandler import DbHandler
from utils import Utils
import json 
from sklearn.cluster import KMeans
import numpy as np
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import random
from geopy.distance import geodesic
import warnings
#warnings.filterwarnings("ignore")

app = Flask(__name__)

db = DbHandler()
zones = []
latlng = []

def perturbate_coordinates(coordinates, n, max_distance):
    perturbed_coords = []
    
    for i in range(n):
        if i == 0:
            perturbed_coords.append(coordinates)
        else:
            distance = random.uniform(0, int(max_distance)*1000)
            
            angle = random.uniform(0, 360)
            
            perturbed_coord = geodesic(meters= distance).destination((coordinates[0],coordinates[1]), bearing=angle)
            
            perturbed_coords.append((perturbed_coord.latitude, perturbed_coord.longitude))
        
    return perturbed_coords
        
    
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/send_position', methods=['POST'])
def send_position():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    latlng.append([latitude, longitude])
    
    return jsonify({'message': 'Position inserted'})
    
@app.route('/upload', methods=['POST'])
def upload():
    if 'collection' not in request.form or ('file' not in request.files and 'folder' not in request.files):
        return jsonify({'error': 'Collection name and either file or folder must be provided'})
    
    collection_name = request.form['collection']
    
    collectionId = db.exec_query("select collection_id from collections c where name = %s", (collection_name,))[0]
    
    if len(latlng) == 0:    
        latlong = Utils.get_coordinates()
    else:
        latlong = latlng[0]
    
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if 'file' in request.files and request.files['file'].filename:
        file = request.files['file']
        
        name = file.filename
        
        file.save('media/temp.png')
        Utils.compress_image('media/temp.png', 'media/temp.png')
        
        bytea = Utils.image_to_bytea('media/temp.png')
        
        saveImageQuery = "INSERT INTO media_files (collection_id, name, image, position, date) VALUES (%s, %s, %s, ST_GeogFromText('POINT(%s %s)'), %s) returning name;"
        
        db.exec_insert_query(saveImageQuery,(collectionId, name, bytea, latlong[1], latlong[0], date,))
        
        return jsonify({'message': 'File uploaded successfully'})
    
    elif 'folder' in request.files and request.files['folder'].filename:
        folder = request.files.getlist('folder')
        
        if 'distance' not in request.form:
            max_distance= 0
        else:
            max_distance = request.form['distance']
        
        coordinates = perturbate_coordinates(latlong, len(folder), max_distance)
        
        for file, coord in zip(folder,coordinates):
            name = Path(file.filename).name
        
            file.save('media/temp.png')
            Utils.compress_image('media/temp.png', 'media/temp.png')
        
            bytea = Utils.image_to_bytea('media/temp.png')
        
            saveImageQuery = "INSERT INTO media_files (collection_id, name, image, position, date) VALUES (%s, %s, %s, ST_GeogFromText('POINT(%s %s)'), %s) returning name;"

            db.exec_insert_query(saveImageQuery,(collectionId, name, bytea, coord[1], coord[0], date,))
            
        return jsonify({'message': 'Folder uploaded successfully'})
    
    return jsonify({'error': 'Unable to upload the file'})

@app.route('/upload_geojson', methods=['POST'])
def upload_geojson():
    file = request.files['file']
    geojson_data = json.loads(file.read())
    
    for feature in geojson_data['features']:
        if feature['geometry']['type'] == 'Polygon':
            zones.append(feature['geometry']['coordinates'])
    
    return jsonify({'message':'GeoJSON uploaded successfully'})

@app.route('/get_photo_data')
def get_photo_data():
    photos_query = "select name, ST_X(position::geometry), ST_Y(position::geometry), image from media_files;"
    photos = db.exec_query(photos_query)
    
    for photo in photos:
        Utils.bytea_to_image(photo[3].tobytes(), f'media/{photo[0]}')
            
        Utils.decompress_image(f'media/{photo[0]}', f'media/{photo[0]}')
        
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [photo[1], photo[2]]  # Use your photo's coordinates
                },
                "properties": {
                    "name": photo[0],  # Include additional properties as needed
                }
            }
            for photo in photos  # Loop through your retrieved photos
        ]
    }

    return jsonify(geojson)

@app.route('/media/<image>')
def media_image(image):
    Utils.resize_image(f'media/{image}', f'media/{image}')
    with open(f'media/{image}', 'rb') as f:
        img = f.read()
    return img

@app.route('/filter_markers', methods=['POST'])
def filter_markers():
    data = request.get_json()
    polygon = data.get('coordinates')
    
    polygon_str = ""
    for point in polygon[0]:
        polygon_str += f"{point[0]} {point[1]},"
    
    polygon_str = polygon_str[:-1]
    photos_query = "select name, ST_X(position::geometry), ST_Y(position::geometry) from media_files;"
    photos = db.exec_query(photos_query)
    
    contained = []
    for photo in photos:
        query = "SELECT ST_Contains(ST_GeomFromText('POLYGON(({}))'), ST_GeomFromText('POINT(%s %s)'));"
        polq = query.format(polygon_str)
        
        is_contained = db.exec_query(polq, (photo[1], photo[2],))[0]
        
        if(is_contained[0]):
            contained.append(photo)
    
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [photo[1], photo[2]]  # Use your photo's coordinates
                },
                "properties": {
                    "name": photo[0],  # Include additional properties as needed
                }
            }
            for photo in contained  # Loop through your retrieved photos
        ]
    }

    return jsonify(geojson)
        
@app.route('/color_zones')
def color_zones():
    photos_query = "select name, ST_X(position::geometry), ST_Y(position::geometry) from media_files;"
    photos = db.exec_query(photos_query)
    
    zones_with_counts = []
    total_photos= 0
    for zone in zones:
        
        polygon_str = ""
        for point in zone[0]:
            polygon_str += f"{point[0]} {point[1]},"
    
        polygon_str = polygon_str[:-1]
        
        query = "SELECT ST_Contains(ST_GeomFromText('POLYGON(({}))'), ST_GeomFromText('POINT(%s %s)'));"
        polq = query.format(polygon_str)
        
        contained = [
            photo for photo in photos
            if db.exec_query(polq, (photo[1], photo[2],))[0][0]
        ]
        
        total_photos+= len(contained)
        zones_with_counts.append((zone, len(contained)))
    
    color_ranges = {
        'low': 0,
        'medium': total_photos // 2,
        'high': total_photos
    }
    
    zones_with_colors= []
    
    for zone, count in zones_with_counts:
        if count <= color_ranges['low']:
            zones_with_colors.append((zone, '#00ff00'))
        elif color_ranges['low'] < count <= color_ranges['medium']:
            zones_with_colors.append((zone,'#ffff00'))
        else:
            zones_with_colors.append((zone, '#ff0000'))
            
    
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "fill": zone[1],
                    "fill-opacity": 1
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": zone[0]  
                }                
            }
            for zone in zones_with_colors  
        ]
    }
    
    return jsonify(geojson)

@app.route('/cluster_markers', methods=['POST'])
def cluster_markers():
    data = request.get_json()
    k = data.get('k')
    
    photos_query = "select name, ST_X(position::geometry), ST_Y(position::geometry) from media_files;"
    photos = db.exec_query(photos_query)
    
    coordinates = []
    
    for photo in photos:
        coordinates.append([photo[1], photo[2]])
        
    if k != 0:
        k = int(k)
    else:
        distorsions = []
        K=range(1,10)
        for i in K:
            if len(coordinates) < i:
                break
            kmeans = KMeans(n_clusters=i, random_state=0)
            kmeans.fit(coordinates)
            distorsions.append(kmeans.inertia_)
        '''    
        plt.plot(K, distorsions, 'bx-')
        plt.xlabel('Values of K')
        plt.ylabel('Distortion')
        plt.title('The Elbow Method using Distortion')
        plt.show()
        '''
        second_derivative = np.diff(np.diff(distorsions))

        elbow_index = np.where(second_derivative == max(second_derivative))[0][0] + 1
        
        k = elbow_index + 1 if second_derivative.any() else 2

    kmeans = KMeans(n_clusters=k, random_state=0)
    kmeans.fit(coordinates)
    
    labels = kmeans.labels_
    
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [photo[1], photo[2]]  # Use your photo's coordinates
                },
                "properties": {
                    "name": photo[0],  
                    "cluster": int(cluster)
                }
            }
            for photo,cluster in zip(photos,labels)  # Loop through your retrieved photos
        ]
    }
    
    return jsonify(geojson)

@app.route('/get_markers')
def get_markers():
    photos_query = "select ST_Y(position::geometry), ST_X(position::geometry) from media_files;"
    photos = db.exec_query(photos_query)
    
    return photos

@app.route('/gallery')
def visualize_gallery():
    return render_template('photos.html')

@app.route('/get_collections_and_photos')
def get_photos_data():
    collections_query = "select collection_id, name from collections"
    
    collections = db.exec_query(collections_query)
    
    collections_photos=[]
    
    for id, name in collections:
        photos_query = "select name from media_files where collection_id=%s"
        
        photos = db.exec_query(photos_query, (id,))
        
        collections_photos.append([id,name,photos])
        
    json = [
            {
                "id": id,
                "name": name,
                "photos": photo
            }
            for id, name, photo in collections_photos  # Loop through your retrieved photos
            ]
    
    return jsonify(json)
    
@app.route('/build_trail', methods=['POST'])
def build_trail():
    data = request.get_json()
    collection_name = data.get('collName')
    
    photos_query = "select ST_X(position::geometry), ST_Y(position::geometry), date from media_files where collection_id=(select collection_id from collections where name=%s)"
    
    photos = db.exec_query(photos_query, (collection_name,))
    
    json = [
        {
            "lat": lat,
            "lng": long,
            "timestamp": date    
        }
        for long, lat, date in photos
    ]
    
    return jsonify(json)

if __name__ == '__main__':
    app.run(debug=True)