import argparse
import signal
import threading
import time
from queue import Queue
from typing import List

from watchdog.observers.inotify import InotifyObserver

from tagger import DATA_BASE_PATH
from tagger.config import init_config
from tagger.dataset.dataset import DatasetHandler, DatasetWorker
from tagger.db.mongo_client import init_db
from tagger.model.model_register import ModelRegister
from tagger.model.model_worker import ModelWorker
from tagger.utils import logger

parser = argparse.ArgumentParser(description='py-photo-tagger cli arguments')
parser.add_argument('-w', '--watch', dest='watch', action='store_true', help='Watch filesystem for changes')
parser.add_argument('-c', '--config', dest='config', help='Model config file')

main_event = threading.Event()
thread_event = threading.Event()


def stop(threads):
    logger.info("Stopping threads")
    thread_event.set()
    for worker in threads:
        if isinstance(worker, InotifyObserver):
            worker.stop()
        worker.join()
    logger.info("Threads stopped")


def signal_handler(signum, frame):
    logger.info("Received signal: %s", signum)
    main_event.set()


def main(watch: bool = False, config_file_path: str = './config.yaml'):

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    config = init_config(config_file_path)

    model_register = ModelRegister(config.models)

    init_db()

    threads = []
    input_queues: List[Queue] = []

    for model_handler in model_register.list_models():
        input_queue = Queue()
        input_queues.append(input_queue)

        worker = ModelWorker(model_handler, input_queue, thread_event)
        worker.start()
        threads.append(worker)

    dataset_worker = DatasetWorker(input_queues, thread_event)
    dataset_worker.start()
    threads.append(dataset_worker)

    if watch:
        observer = InotifyObserver()
        handler = DatasetHandler(input_queues)
        observer.schedule(handler, DATA_BASE_PATH, recursive=True)
        observer.start()
        threads.append(observer)
        logger.info("Started file system watchdog")
    else:
        dataset_worker.join()
        main_event.set()
        logger.info("Dataset processing completed")

    try:
        while not main_event.is_set():
            time.sleep(.1)
        stop(threads)
    except KeyboardInterrupt:
        # Ctrl-C handling and send kill to threads
        main_event.set()
        stop(threads)


if __name__ == '__main__':
    args = parser.parse_args()

    main(args.watch, args.config)
