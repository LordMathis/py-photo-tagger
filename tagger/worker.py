import logging
import os
import threading
from typing import Dict

import torch
from PIL import Image
from torch.utils.data import Dataset, DataLoader

from tagger import DATA_BASE_PATH, utils
from tagger.model.abstract_model_handler import AbstractModelHandler


class Worker(threading.Thread):

    def __init__(self, model_handler: AbstractModelHandler, loader: DataLoader, photo_tags: Dict = None):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self._model_handler = model_handler
        self._model_name = model_handler.get_model_name()
        self._photo_tags = photo_tags if photo_tags is not None else {}

        self._loader = loader

    def run(self) -> None:
        with torch.no_grad():
            for batch_idx, (image, filepath) in enumerate(self._loader):
                filepath = filepath[0]
                prediction = self._model_handler.predict(image)
                if filepath not in self._photo_tags:
                    self._photo_tags[filepath] = {}
                self._photo_tags[filepath][self._model_name] = prediction

        utils.write_json_file('./taggs.json', self._photo_tags)
