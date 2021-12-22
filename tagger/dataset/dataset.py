# Copyright (c) Konica Minolta Business Solutions. All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
import hashlib
import logging
import os
import threading
from queue import Queue
from typing import List

import cv2
import numpy as np
import torch
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from tagger import DATA_BASE_PATH
from tagger.db.schema import PhotoDocument
from tagger.geolocate import get_location


def process_image(img_path: str, input_queues: List[Queue]):
    try:
        with open(img_path, "rb") as f:
            img_bytes = f.read()
            img_hash = hashlib.sha256(img_bytes).hexdigest()

            photo = PhotoDocument.objects(hash=img_hash).first()
            if photo is None:
                photo = PhotoDocument(hash=img_hash, filepath=img_path, models={})

            img_loc = get_location(f)
            if img_loc:
                photo.latitude = img_loc['latitude']
                photo.longitude = img_loc['longitude']
                photo.city = img_loc['city']
                photo.country = img_loc['country']

            np_arr = np.frombuffer(img_bytes, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            for queue in input_queues:
                queue.put((photo, img_path, image))
    except IOError:
        logging.getLogger(__name__).exception("Exception reading image file %s" % img_path)


class DatasetHandler(FileSystemEventHandler):

    def __init__(self, input_queues: List[Queue]):
        self._input_queues = input_queues

    def on_any_event(self, event: FileSystemEvent):
        if event.is_directory:
            return
        process_image(event.src_path, self._input_queues)


class DatasetWorker(threading.Thread):

    def __init__(self, input_queues: List[Queue]):
        super().__init__()

        self._input_queues = input_queues

    def run(self) -> None:
        for path, _, files in os.walk(DATA_BASE_PATH):
            for file in files:
                img_path = os.path.join(path, file)
                process_image(img_path, self._input_queues)