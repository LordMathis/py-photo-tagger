import os
from typing import Dict, List

from tagger import MODELS_BASE_PATH
from tagger.model.abstract_model_handler import AbstractModelHandler
from tagger.model.imagenet_handler import ImageNetHandler
from tagger.model.places365_handler import MODEL_BASE_NAME as PLACES365_MODEL, Places365Handler


class ModelRegister:

    models: Dict[str, AbstractModelHandler] = {}

    def register(self, model: AbstractModelHandler):
        model.load()
        self.models[model.get_model_name()] = model

    def find_all_models(self):
        self.register(ImageNetHandler())
        for path, dirs, files in os.walk(MODELS_BASE_PATH):
            for file in files:
                if PLACES365_MODEL in file:
                    places_model = Places365Handler(os.path.join(path, file))
                    self.register(places_model)

    def list_models(self) -> List[AbstractModelHandler]:
        return list(self.models.values())