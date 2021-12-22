import logging
import threading
from queue import Queue

import cv2
import numpy as np
import torch

from tagger.db.mongo_client import populate_tag_list
from tagger.db.schema import ModelDocument, TagDocument
from tagger.model.abstract_model_handler import AbstractModelHandler


class ModelWorker(threading.Thread):

    def __init__(self, model_handler: AbstractModelHandler, input_queue: Queue):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self._model_handler = model_handler
        self._model_name = model_handler.get_model_name()

        self._input_queue = input_queue

        populate_tag_list(model_handler.get_classes())

    def run(self) -> None:
        with torch.no_grad():

            while True:

                photo, filepath, img_bytes = self._input_queue.get()

                if self._model_name in photo.models:
                    continue

                prediction = self._model_handler.process(image)

                model = ModelDocument(name=self._model_name)
                tags = [TagDocument(name=name, probability=prob) for (name, prob) in prediction.items()]
                model.tags = tags
                photo.models[self._model_name] = model
                photo.save()
