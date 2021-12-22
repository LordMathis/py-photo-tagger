import os
import threading
from queue import Queue
from typing import BinaryIO

import exifread
import reverse_geocode

from tagger import DATA_BASE_PATH
from tagger.db.schema import PhotoDocument


def __convert_to_degress(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
    :param value:
    :type value: exifread.utils.Ratio
    :rtype: float
    """
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)

    return d + (m / 60.0) + (s / 3600.0)


def _get_gps_coords(file: BinaryIO):
    """
    returns gps data if present other wise returns empty dictionary
    """
    tags = exifread.process_file(file)
    latitude = tags.get('GPS GPSLatitude')
    latitude_ref = tags.get('GPS GPSLatitudeRef')
    longitude = tags.get('GPS GPSLongitude')
    longitude_ref = tags.get('GPS GPSLongitudeRef')

    if latitude:
        lat_value = __convert_to_degress(latitude)
        if latitude_ref.values != 'N':
            lat_value = -lat_value
    else:
        return None

    if longitude:
        lon_value = __convert_to_degress(longitude)
        if longitude_ref.values != 'E':
            lon_value = -lon_value
    else:
        return None

    return lat_value, lon_value


def get_location(file: BinaryIO):
    coords = _get_gps_coords(file)
    if coords:
        location = reverse_geocode.get(coords)
        return {
            "latitude": coords[0],
            "longitude": coords[1],
            "city": location["city"],
            "country": location["country"]
        }
