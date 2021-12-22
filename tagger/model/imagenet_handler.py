from typing import Dict

import PIL
import torch
from PIL.Image import Image
from torch.nn import functional
from torchvision import models

from tagger.dataset import imagenet_classes
from tagger.model.abstract_model_handler import AbstractModelHandler
from tagger.utils import centre_crop


class ImageNetHandler(AbstractModelHandler):

    def __init__(self):
        self._model_name = "EfficientNet_B7_ImageNet"
        self._model = models.efficientnet_b7(pretrained=True)
        self._classes = imagenet_classes.classes
        self.transform = centre_crop

    def load(self) -> None:
        if torch.cuda.is_available():
            self._model.cuda()
        self._model.eval()
        self._loaded = True

    def predict(self, image: torch.Tensor) -> Dict:

        out = self._model(image)
        _, indices = torch.sort(out, descending=True)
        percentage = functional.softmax(out, dim=1)[0] * 100

        res = {}

        for idx in indices[0][:5]:
            res[self._classes[idx.item()]] = '{:.3f}'.format(percentage[idx].item())
        return res
