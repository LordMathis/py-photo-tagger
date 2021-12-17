# Copyright (c) Konica Minolta Business Solutions. All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
import threading
from queue import Queue

from tagger.db.schema import PhotoDocument, ModelDocument, TagDocument


class MongoWorker(threading.Thread):

    def __init__(self, queue: Queue):
        super().__init__()

        self._queue = queue

    def run(self) -> None:

        while True:

            filepath, model_name, prediction = self._queue.get()

            photo = PhotoDocument.objects(filepath=filepath).first()
            if photo is None:
                photo = PhotoDocument(filepath=filepath, models={})
                model = ModelDocument(name=model_name)
            else:
                model = photo.models.get(model_name, ModelDocument(name=model_name))

            tags = [TagDocument(name=name, probability=prob) for (name, prob) in prediction.items()]
            model.tags = tags
            photo.models[model_name] = model
            photo.save()
