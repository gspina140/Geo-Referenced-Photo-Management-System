from PIL import Image as PILImage
import geocoder

class Utils:
    def __init__(self) -> None:
        pass
    
    def image_to_bytea(image_path):
        try:
            with open(image_path, "rb") as image:
                bytea = image.read()
            return bytea
        except IOError as e:
            print(f"Unable to read: {str(e)}")
            return None

    def bytea_to_image(bytea, output_path):
        try:
            with open(output_path, "wb") as image:
                image.write(bytea)
            return True
        except IOError as e:
            print(f"Unable to write: {str(e)}")
            return False
        
    def compress_image(input_path, output_path, quality=85):
        try:
            img = PILImage.open(input_path)
            img.save(output_path, "WebP", optimize=True, quality=quality)
            return True
        except Exception as e:
            print(f"Error compressing the image: {str(e)}")
            return False
        
    def decompress_image(input_path, output_path, format="JPEG"):
        try:
            img = PILImage.open(input_path)
            img.save(output_path, format)
            return True
        except Exception as e:
            print(f"Unable to decompress : {str(e)}")
            return False
        
    def resize_image(path, dest):
        try:
            img = PILImage.open(path)
            img = img.resize((360,360))
            img.save(dest)
            return True
        except Exception as e:
            print(f"Unable to resize : {str(e)}")
            return False
        
    def get_location():
        location = geocoder.ip("me")
        return location.address
    
    def get_coordinates():
        location = geocoder.ip("me")
        return location.latlng