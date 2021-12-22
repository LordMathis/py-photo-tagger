import logging
from abc import abstractmethod
from typing import Dict, List

import torch
from torch import nn


class AbstractModelHandler:

    _model_name: str
    _model_loaded: bool = False
    _model: nn.Module
    _logger = logging.getLogger(__name__)
    _classes: Dict[int, str]
    _loaded: bool = False

    transform = None

    def process(self, img):

        if not self._loaded:
            self.load()

        img_tensor = torch.from_numpy(img)
        image = img_tensor.unsqueeze(0)

        if torch.cuda.is_available():
            image = image.to('cuda')

        if self.transform:
            image = self.transform(image)

        return self.predict(image)

    @abstractmethod
    def predict(self, img) -> Dict:
        pass

    @abstractmethod
    def load(self) -> None:
        pass

    def get_model_name(self) -> str:
        return self._model_name

    def get_classes(self) -> Dict[int, str]:
        return self._classes
