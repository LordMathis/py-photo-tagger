import threading
from queue import Queue
from typing import List

from watchdog.observers.inotify import InotifyObserver

from tagger import DATA_BASE_PATH
from tagger.dataset.dataset import DatasetHandler, DatasetWorker
from tagger.db.mongo_client import init_db
from tagger.model.model_register import ModelRegister
from tagger.model.model_worker import ModelWorker


def main():
    model_register = ModelRegister()
    model_register.find_all_models()

    init_db()

    threads = []

    input_queues: List[Queue] = []

    for model_handler in model_register.list_models():
        input_queue = Queue()
        input_queues.append(input_queue)

        worker = ModelWorker(model_handler, input_queue)
        worker.start()
        threads.append(worker)

    dataset_worker = DatasetWorker(input_queues)
    dataset_worker.start()
    threads.append(dataset_worker)

    observer = InotifyObserver()
    observer.schedule(DatasetHandler, DATA_BASE_PATH, recursive=True)
    observer.start()
    threads.append(observer)

    for worker in threads:
        worker.join()


if __name__ == '__main__':
    main()
