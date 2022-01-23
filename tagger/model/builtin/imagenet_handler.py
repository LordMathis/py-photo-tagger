from typing import Dict

import torch
from pydantic import BaseModel
from torch.nn import functional
from torchvision import models

from tagger.dataset import imagenet_classes
from tagger.utils import centre_crop


class ImageNetConfig(BaseModel):
    model_arch: str = "efficientnet_b1"


class ImageNetHandler:
    model_name = "ImageNet"

    def __init__(self, config: Dict):
        config = ImageNetConfig(**config)
        self._model = self._load(config.model_arch)
        self._model_loaded = True

        self.classes = imagenet_classes.classes
        self.transform = centre_crop

    def _load(self, model_arch):

        if not hasattr(models, model_arch.lower()):
            return

        model = getattr(models, model_arch.lower())(pretrained=True)

        if torch.cuda.is_available():
            model.cuda()
        model.eval()

        return model

    def predict(self, image: torch.Tensor) -> Dict:

        out = self._model(image)
        _, indices = torch.sort(out, descending=True)
        percentage = functional.softmax(out, dim=1)[0] * 100

        res = {}

        for idx in indices[0][:5]:
            res[self.classes[idx.item()]] = '{:.3f}'.format(percentage[idx].item())
        return res
