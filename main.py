from torch.utils.data import DataLoader

from tagger import utils
from tagger.dataset.photo_dataset import PhotoDataset
from tagger.db.mongo_client import MongoClient
from tagger.model.model_register import ModelRegister
from tagger.worker import Worker


def main():
    model_register = ModelRegister()
    model_register.find_all_models()

    client = MongoClient()

    json_data = None
    try:
        json_data = utils.read_json_file('./taggs.json')
    except OSError:
        pass

    workers = []
    for model_handler in model_register.list_models():
        dataset = PhotoDataset(model_handler.transform)
        loader = DataLoader(dataset)

        worker = Worker(model_handler, loader, json_data, client)
        worker.start()
        workers.append(worker)

    for worker in workers:
        worker.join()


if __name__ == '__main__':
    main()
