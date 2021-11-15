from torch.utils.data import DataLoader
from torchvision import datasets

from tagger import utils, DATA_BASE_PATH
from tagger.dataset.photo_dataset import PhotoDataset
from tagger.model.model_register import ModelRegister
from tagger.worker import Worker

model_register = ModelRegister()
model_register.find_all_models()

json_data = None
try:
    json_data = utils.read_json_file('./taggs.json')
except OSError:
    pass

workers = []
for model_handler in model_register.list_models():
    dataset = PhotoDataset(model_handler.transform)
    loader = DataLoader(dataset)

    worker = Worker(model_handler, loader, json_data)
    worker.start()
    workers.append(worker)

for worker in workers:
    worker.join()
