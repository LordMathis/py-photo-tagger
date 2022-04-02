import argparse
import signal
import threading
import time
from queue import Queue
from typing import List

from watchdog.observers.inotify import InotifyObserver

from tagger import DATA_BASE_PATH
from tagger.dataset.dataset import DatasetHandler, DatasetWorker
from tagger.model.model_register import ModelRegister
from tagger.model.model_worker import ModelWorker
from tagger.utils import logger


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


def main(watch: bool = False, ):

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    model_register = ModelRegister()
    model_register.find_all_models()

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


parser = argparse.ArgumentParser(description='py-photo-tagger cli arguments')
parser.add_argument('-w', '--watch', dest='watch', action='store_true', help='Watch filesystem for changes')

main_event = threading.Event()
thread_event = threading.Event()

if __name__ == '__main__':
    args = parser.parse_args()

    main(args.watch)
