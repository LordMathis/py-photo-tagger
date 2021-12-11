import logging
import threading

import torch
from torch.utils.data import DataLoader

from tagger.db.mongo_client import populate_tag_list
from tagger.db.schema import PhotoDocument, TagDocument, ModelDocument
from tagger.model.abstract_model_handler import AbstractModelHandler


class Worker(threading.Thread):

    def __init__(self, model_handler: AbstractModelHandler, loader: DataLoader):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self._model_handler = model_handler
        self._model_name = model_handler.get_model_name()

        self._loader = loader

        populate_tag_list(model_handler.get_classes())

    def run(self) -> None:
        with torch.no_grad():
            for batch_idx, (image, filepath) in enumerate(self._loader):
                filepath = filepath[0]
                prediction = self._model_handler.predict(image)

                photo = PhotoDocument.objects(filepath=filepath).first()
                if photo is None:
                    photo = PhotoDocument(filepath=filepath, models={})
                    model = ModelDocument(name=self._model_name)
                else:
                    model = photo.models.get(self._model_name, ModelDocument(name=self._model_name))

                tags = [TagDocument(name=name, probability=prob) for (name, prob) in prediction.items()]
                model.tags = tags
                photo.models[self._model_name] = model
                photo.save()
