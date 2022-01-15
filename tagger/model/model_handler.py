from dataclasses import dataclass
from typing import Dict, List, Protocol

from torch import nn


@dataclass
class ModelHandler(Protocol):

    model: nn.Module
    model_name: str
    classes: List[str]
    transform = None

    def predict(self, img) -> Dict:
        ...
