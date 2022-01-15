from typing import Dict

import torch
from torch.nn import functional
from torchvision import models

from tagger.config import ModelConfig
from tagger.dataset import imagenet_classes
from tagger.utils import centre_crop


class ImageNetHandler:

    def __init__(self, config: ModelConfig):
        self.model_name = "EfficientNet_B7_ImageNet"
        self.model = models.efficientnet_b7(pretrained=True)
        self.classes = imagenet_classes.classes
        self.transform = centre_crop

        self._load()

    def _load(self) -> None:
        if torch.cuda.is_available():
            self._model.cuda()
        self._model.eval()
        self._model_loaded = True

    def predict(self, image: torch.Tensor) -> Dict:

        out = self._model(image)
        _, indices = torch.sort(out, descending=True)
        percentage = functional.softmax(out, dim=1)[0] * 100

        res = {}

        for idx in indices[0][:5]:
            res[self._classes[idx.item()]] = '{:.3f}'.format(percentage[idx].item())
        return res
