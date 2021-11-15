import os
from pathlib import Path

import torch
from torch import tensor, Tensor
from torch.autograd import Variable
from torch.nn import functional
from torchvision import models, transforms

from tagger.model.abstract_model_handler import AbstractModelHandler

MODEL_BASE_NAME = 'places365.pth.tar'


def load_classes(classes_path):
    # load the class label
    file_name = os.path.join(classes_path, 'categories_places365.txt')
    classes = []
    with open(file_name) as class_file:
        for line in class_file:
            classes.append(line.strip().split(' ')[0][3:])
    classes = tuple(classes)
    return classes


centre_crop = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


class Places365Handler(AbstractModelHandler):

    def __init__(self, model_path: str):
        self._model_name: str = model_path.split('/')[-1]
        self._model_arch: str = self._model_name.split('_')[0]
        self._model_path: str = model_path
        self._classes = load_classes(Path(model_path).parent.absolute())

        self.transform = centre_crop

    def predict(self, image_data: Tensor):
        if not self._model_loaded:
            self._logger.warning("Model is not loaded.")
            return None

        # input_img = Variable(centre_crop(image_data).unsqueeze(0))

        if torch.cuda.is_available():
            image_data = image_data.to('cuda')

        logit = self._model.forward(image_data)
        h_x = functional.softmax(logit, 1).data.squeeze()
        probs, idx = h_x.sort(0, True)

        res = {}

        for i in range(0, 5):
            res[self._classes[idx[i]]] = '{:.3f}'.format(probs[i])

        return res

    def load(self):
        if self._model_loaded:
            return

        model = models.__dict__[self._model_arch](num_classes=365)

        checkpoint = torch.load(self._model_path, map_location=lambda storage, loc: storage)
        state_dict = {str.replace(k, 'module.', ''): v for k, v in checkpoint['state_dict'].items()}
        model.load_state_dict(state_dict)

        if torch.cuda.is_available():
            model.cuda()

        self._model_loaded = True
        self._model = model
