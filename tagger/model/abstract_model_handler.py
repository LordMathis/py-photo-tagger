import logging
from abc import abstractmethod
from typing import Dict

from torch import nn


class AbstractModelHandler:

    _model_name: str
    _model_loaded: bool = False
    _model: nn.Module
    _logger = logging.getLogger(__name__)

    transform = None

    @abstractmethod
    def predict(self, img) -> Dict:
        pass

    @abstractmethod
    def load(self) -> None:
        pass

    def get_model_name(self) -> str:
        return self._model_name
