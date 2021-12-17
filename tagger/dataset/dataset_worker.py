# Copyright (c) Konica Minolta Business Solutions. All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
import os
import threading
from queue import Queue
from typing import List

from tagger import DATA_BASE_PATH
from tagger.dataset.dataset_handler import process_image


class DatasetWorker(threading.Thread):

    def __init__(self, input_queues: List[Queue]):
        super().__init__()

        self._input_queues = input_queues

    def run(self) -> None:
        for path, _, files in os.walk(DATA_BASE_PATH):
            for file in files:
                img_path = os.path.join(path, file)
                process_image(img_path, self._input_queues)
