import queue
import threading
from queue import Queue

import numpy as np
import torch
from sqlalchemy.orm import Session

from tagger.db.db import Database
from tagger.db.models import Photo, Model, ModelPhotoStatus, PhotoTag, ModelTag
from tagger.ml.abstract_model_handler import AbstractModelHandler
from tagger.utils import logger


class ModelWorker(threading.Thread):

    def __init__(self, model_handler: AbstractModelHandler, input_queue: Queue, db: Database,
                 thread_event: threading.Event):
        super().__init__()
        self._model_handler = model_handler
        self._model_name = model_handler.get_model_name()
        self._db = db
        self._event = thread_event

        self._input_queue = input_queue

    def run(self) -> None:
        sess: Session
        with torch.no_grad() and self._db.session() as sess:
            while not self._event.is_set():
                try:
                    print('Hello')
                    filepath: str
                    img_hash: str
                    image: np.ndarray
                    filepath, img_hash, image = self._input_queue.get(timeout=.1)

                    photo: Photo = sess.query(Photo).get(img_hash)

                    model: Model
                    model_status: ModelPhotoStatus
                    model, model_status = (sess.query(Model, ModelPhotoStatus)
                                           .join(ModelPhotoStatus, isouter=True)
                                           .filter(Model.name == self._model_name)
                                           .filter(ModelPhotoStatus.photo == photo)
                                           ).first()

                    if model_status is None:
                        model_status = ModelPhotoStatus()
                        model_status.model = model
                        model_status.photo = photo

                    if model_status.status:
                        continue

                    logger.info("Running prediction on file %s by ml %s" % (filepath, self._model_name))
                    prediction = self._model_handler.process(image)

                    for (value, prob) in prediction.items():
                        tag = sess.query(ModelTag).filter(ModelTag.model == model).filter(
                            ModelTag.name == value).firts()

                        photo_tag = PhotoTag()
                        photo_tag.tag = tag
                        photo_tag.photo = photo
                        photo_tag.probability = prob

                        sess.add(photo_tag)

                    model_status.status = True
                    sess.add(model_status)

                    sess.commit()

                except queue.Empty:
                    pass
