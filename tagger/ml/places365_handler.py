import os
from pathlib import Path
from typing import Dict

import torch
from torch import Tensor
from PIL.Image import Image
from torch.nn import functional
from torchvision import models

from tagger.ml.abstract_model_handler import AbstractModelHandler
from tagger.utils import centre_crop

MODEL_BASE_NAME = 'places365.pth.tar'


def load_classes(classes_path):
    # load the class label
    file_name = os.path.join(classes_path, 'categories_places365.txt')
    classes = {}
    with open(file_name) as class_file:
        for line in class_file:
            class_line = line.strip().split(' ')
            class_idx = int(class_line[1])
            class_name = class_line[0][3:]
            classes[class_idx] = class_name
    return classes


class Places365Handler(AbstractModelHandler):

    def __init__(self, model_path: str):
        self._model_name: str = model_path.split('/')[-1].split('.')[0]
        self._model_arch: str = self._model_name.split('_')[0]
        self._model_path: str = model_path
        self._classes = load_classes(Path(model_path).parent.absolute())

        self.transform = centre_crop

    def predict(self, image: torch.Tensor) -> Dict:

        logit = self._model.forward(image)
        h_x = functional.softmax(logit, 1).data.squeeze()
        probs, idx = h_x.sort(0, True)

        res = {}

        for i in range(0, 5):
            res[self._classes[idx[i].item()]] = probs[i]  # '{:.3f}'.format(probs[i])

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
        self._model.eval()
