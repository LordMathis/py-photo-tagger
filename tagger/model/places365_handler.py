import os

import torch
from torch.autograd import Variable
from torch.nn import functional
from torchvision import models, transforms

from tagger import MODELS_BASE_PATH
from tagger.model.abstract_handler import AbstractHandler


def load_model(model_name):
    model_arch = model_name.split('_')[0]
    model_fn = [os.path.join(dp, f) for dp, dn, filenames in os.walk(MODELS_BASE_PATH) for f in filenames if
                f == model_name][0]

    model = models.__dict__[model_arch](num_classes=365)

    checkpoint = torch.load(model_fn, map_location=lambda storage, loc: storage)
    state_dict = {str.replace(k, 'module.', ''): v for k, v in checkpoint['state_dict'].items()}
    model.load_state_dict(state_dict)

    return model


def load_classes():
    # load the class label
    file_name = os.path.join(MODELS_BASE_PATH, 'categories_places365.txt')
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


class Places365Handler(AbstractHandler):

    def __init__(self, model_filename: str):
        self._model_arch: str = model_filename.split('_')[0]
        self._model_name: str = model_filename.split('/')[-1]
        self._model_fn: str = model_filename
        self._model = load_model(model_filename)
        self._classes = load_classes()

    def predict(self, image_data):
        # forward pass
        input_img = Variable(centre_crop(image_data).unsqueeze(0))
        logit = self._model.forward(input_img)
        h_x = functional.softmax(logit, 1).data.squeeze()
        probs, idx = h_x.sort(0, True)

        res = {self._model_name: {}}

        for i in range(0, 5):
            res[self._model_name][self._classes[idx[i]]] = '{:.3f}'.format(probs[i])

        return res
