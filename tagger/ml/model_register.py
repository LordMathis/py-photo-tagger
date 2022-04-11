import os
from typing import Dict, List

from sqlalchemy.orm import Session

from tagger import MODELS_BASE_PATH
from tagger.db.db import Database
from tagger.db.models import Model, ModelTag
from tagger.ml.abstract_model_handler import AbstractModelHandler
from tagger.ml.imagenet_handler import ImageNetHandler
from tagger.ml.places365_handler import MODEL_BASE_NAME as PLACES365_MODEL, Places365Handler


class ModelRegister:
    models: Dict[str, AbstractModelHandler] = {}

    def __init__(self, db: Database):
        self._db = db

    def register(self, model: AbstractModelHandler):
        sess: Session
        with self._db.session() as sess:
            model.load()

            db_model = sess.query(Model).filter(Model.name == model.get_model_name()).first()

            if db_model is None:
                db_model = Model()
                db_model.name = model.get_model_name()
                db_model.version = 1
                sess.add(db_model)
                sess.commit()

            for tag in model.get_classes().values():
                db_tag = sess.query(ModelTag).filter(ModelTag.model == db_model).filter(ModelTag.name == tag).first()
                if db_tag is None:
                    db_tag = ModelTag()
                    db_tag.model = db_model
                    db_tag.name = tag
                    sess.add(db_tag)

            self.models[model.get_model_name()] = model
            sess.commit()

    def find_all_models(self):
        self.register(ImageNetHandler())
        for path, dirs, files in os.walk(MODELS_BASE_PATH):
            for file in files:
                if PLACES365_MODEL in file:
                    places_model = Places365Handler(os.path.join(path, file))
                    self.register(places_model)

    def list_models(self) -> List[AbstractModelHandler]:
        return list(self.models.values())
