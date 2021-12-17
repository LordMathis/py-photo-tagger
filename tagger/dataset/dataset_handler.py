# Copyright (c) Konica Minolta Business Solutions. All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
import logging
from queue import Queue
from typing import List

import PIL.Image
from PIL import Image
from watchdog.events import FileSystemEventHandler, FileSystemEvent


def process_image(img_path: str, input_queues: List[Queue]):
    try:
        image: PIL.Image.Image = Image.open(img_path)
        for queue in input_queues:
            queue.put((img_path, image))
    except IOError:
        logging.getLogger(__name__).exception("Exception reading image file")


class DatasetHandler(FileSystemEventHandler):

    def __init__(self, input_queues: List[Queue]):
        self._input_queues = input_queues

    def on_any_event(self, event: FileSystemEvent):
        if event.is_directory:
            return
        process_image(event.src_path, self._input_queues)
