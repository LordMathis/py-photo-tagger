import logging
import queue
import threading
from queue import Queue

import numpy as np
import torch

from tagger.db.mongo_client import populate_tag_list
from tagger.db.schema import TagSchema, PhotoSchema
from tagger.model.abstract_model_handler import AbstractModelHandler
from tagger.utils import logger


class ModelWorker(threading.Thread):

    def __init__(self, model_handler: AbstractModelHandler, input_queue: Queue, thread_event: threading.Event):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self._model_handler = model_handler
        self._model_name = model_handler.get_model_name()
        self._event = thread_event

        self._input_queue = input_queue

        populate_tag_list(model_handler.get_classes())

    def run(self) -> None:
        with torch.no_grad():
            while not self._event.is_set():
                try:
                    photo: PhotoSchema
                    filepath: str
                    image: np.ndarray
                    photo, filepath, image = self._input_queue.get(timeout=.1)

                    # if self._model_name in photo.models:
                    #     logger.info("File %s already tagged by model %s. Skipping" % (filepath, self._model_name))
                    #     continue

                    logger.info("Running prediction on file %s by model %s" % (filepath, self._model_name))
                    prediction = self._model_handler.process(image)

                    tags = [TagSchema(value=value, probability=prob, model_name=self._model_name)
                            for (value, prob) in prediction.items()]
                    photo.tags += tags
                    photo.save()
                except queue.Empty:
                    pass
