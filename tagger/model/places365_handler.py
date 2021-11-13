import os

import torch
from torch.autograd import Variable
from torch.nn import functional
from torchvision import models, transforms

from tagger import MODELS_BASE_PATH


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
    if not os.access(file_name, os.W_OK):
        synset_url = 'https://raw.githubusercontent.com/csailvision/places365/master/categories_places365.txt'
        os.system('wget ' + synset_url)
    classes = list()
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


class Places365Handler:

    def __init__(self, model_name: str):
        self._model_arch: str = model_name.split('_')[0]
        self._model_fn: str = model_name
        self._model = load_model(model_name)
        self._classes = load_classes()

    def predict(self, image_data):
        # forward pass
        input_img = Variable(centre_crop(image_data).unsqueeze(0))
        logit = self._model.forward(input_img)
        h_x = functional.softmax(logit, 1).data.squeeze()
        probs, idx = h_x.sort(0, True)

        print('{} prediction:'.format(self._model_arch))
        # output the prediction
        for i in range(0, 5):
            print('{:.3f} -> {}'.format(probs[i], self._classes[idx[i]]))
