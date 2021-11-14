from abc import abstractmethod
from typing import Dict


class AbstractHandler:

    _model_name: str

    @abstractmethod
    def predict(self, img) -> Dict:
        pass

    def get_model_name(self):
        return self._model_name
