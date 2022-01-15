import logging
import queue
import threading
from queue import Queue

import numpy as np
import torch

from tagger.db.mongo_client import populate_tag_list
from tagger.db.schema import TagSchema, PhotoSchema
from tagger.model.model_handler import ModelHandler
from tagger.utils import logger


class ModelWorker(threading.Thread):

    def __init__(self, model_handler: ModelHandler, input_queue: Queue, thread_event: threading.Event):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self._model_handler = model_handler
        self._event = thread_event

        self._input_queue = input_queue

        populate_tag_list(model_handler.classes)

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

                    if self._model_handler.transform:
                        image: torch.Tensor = self._model_handler.transform(image)
                    else:
                        image: torch.Tensor = torch.from_numpy(image)

                    image: torch.Tensor = image.unsqueeze(0)

                    if torch.cuda.is_available():
                        image = image.to('cuda')

                    prediction = self._model_handler.predict(image)

                    tags = [TagSchema(value=value, probability=prob, model_name=self._model_handler.model_name)
                            for (value, prob) in prediction.items()]

                    photo.tags += tags
                    photo.save()
                except queue.Empty:
                    pass
