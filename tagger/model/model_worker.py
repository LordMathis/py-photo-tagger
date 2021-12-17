import logging
import threading
from queue import Queue

import torch
from torch.utils.data import DataLoader

from tagger.db.mongo_client import populate_tag_list
from tagger.db.schema import PhotoDocument, TagDocument, ModelDocument
from tagger.model.abstract_model_handler import AbstractModelHandler


class ModelWorker(threading.Thread):

    def __init__(self, model_handler: AbstractModelHandler, input_queue: Queue, result_queue: Queue):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self._model_handler = model_handler
        self._model_name = model_handler.get_model_name()

        self._input_queue = input_queue
        self._result_queue = result_queue

        populate_tag_list(model_handler.get_classes())

    def run(self) -> None:
        with torch.no_grad():

            while True:

                filepath, image = self._input_queue.get()
                prediction = self._model_handler.predict(image)
                self._result_queue.put((filepath, self._model_name, prediction))
