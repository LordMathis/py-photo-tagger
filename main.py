import threading

from torch.utils.data import DataLoader

from tagger.dataset.photo_dataset import PhotoDataset
from tagger.db.mongo_client import init_db
from tagger.geolocate import geolocate_all
from tagger.model.model_register import ModelRegister
from tagger.worker import Worker


def main():
    model_register = ModelRegister()
    model_register.find_all_models()

    init_db()
    # geolocate_all()

    workers = []

    for model_handler in model_register.list_models():
        dataset = PhotoDataset(model_handler.transform)
        loader = DataLoader(dataset)

        worker = Worker(model_handler, loader)
        worker.start()
        workers.append(worker)

    th = threading.Thread(target=geolocate_all)
    th.start()
    workers.append(th)

    for worker in workers:
        worker.join()


if __name__ == '__main__':
    main()
