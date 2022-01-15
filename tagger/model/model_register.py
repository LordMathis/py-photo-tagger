import importlib.util
import inspect
from typing import Dict, List

from tagger.config import ModelConfig
from tagger.db.mongo_client import populate_tag_list
from tagger.model.model_handler import ModelHandler


class ModelRegister:

    models: Dict[str, ModelHandler] = {}

    def __init__(self, models: List[ModelConfig]):

        for model in models:
            spec = importlib.util.spec_from_file_location(model.module_name, model.module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            plugin_class = [obj for name, obj in inspect.getmembers(module, inspect.isclass) if hasattr(obj, 'predict')][0]
            plugin_instance = plugin_class(model)

            self.register(plugin_instance)

    def register(self, model: ModelHandler):
        self.models[model.model_name] = model
        populate_tag_list(model.classes)

    def list_models(self) -> List[ModelHandler]:
        return list(self.models.values())
