import os

import reverse_geocoder as rg
from GPSPhoto import gpsphoto
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

from tagger import DATA_BASE_PATH


def get_location():
    for path, _, files in os.walk(DATA_BASE_PATH):
        for file in files:
            img_path = os.path.join(path, file)

            gps_data = gpsphoto.getGPSData(img_path)

            print(gps_data)
