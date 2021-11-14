import logging
import os
import threading
from typing import Dict

from PIL import Image

from tagger import DATA_BASE_PATH, utils
from tagger.model.abstract_model_handler import AbstractModelHandler


class Worker(threading.Thread):

    def __init__(self, model_handler: AbstractModelHandler, photo_tags: Dict = None):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self._model_handler = model_handler
        self._model_name = model_handler.get_model_name()
        self._photo_tags = photo_tags if photo_tags is not None else {}

    def run(self) -> None:
        for path, _, files in os.walk(DATA_BASE_PATH):
            for file in files:
                filepath = os.path.join(path, file)
                self._photo_tags.setdefault(filepath, {})
                if filepath in self._photo_tags and self._model_name in self._photo_tags[filepath]:
                    self._logger.debug('File {} is already tagged by {} model. Skipping'.format(filepath, self._model_name))
                    continue

                try:
                    img = Image.open(filepath)
                    prediction = self._model_handler.predict(img)
                    self._photo_tags[filepath][self._model_name] = prediction[self._model_name]
                except IOError:
                    self._logger.debug('File {} is not a valid image. Skipping'.format(filepath))

        utils.write_json_file('./taggs.json', self._photo_tags)
