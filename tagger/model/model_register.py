import importlib.util
import inspect
from typing import Dict, List

from tagger.config import ModelConfig
from tagger.db.mongo_client import populate_tag_list
from tagger.model.builtin import BUILTIN_MODEL_NAMES, Places365Handler, ImageNetHandler
from tagger.model.model_handler import ModelHandler


class ModelRegister:

    models: Dict[str, ModelHandler] = {}

    def __init__(self, models: List[ModelConfig]):

        for model in models:
            if model.model_name in BUILTIN_MODEL_NAMES:
                self.register_builtin_model(model)
            else:
                self.register_plugin_model(model)

    def register_plugin_model(self, model_config: ModelConfig):
        spec = importlib.util.spec_from_file_location(model_config.module_name, model_config.module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        plugin_class = [obj for name, obj in inspect.getmembers(module, inspect.isclass) if hasattr(obj, 'predict')][0]
        plugin_instance = plugin_class(model_config.dict())

        self.models[model_config.model_name] = plugin_instance
        populate_tag_list(plugin_instance.classes)

    def register_builtin_model(self, model_config: ModelConfig):
        model = None
        if model_config.model_name == Places365Handler.model_name:
            model = Places365Handler(model_config.dict())
        elif model_config.model_name == ImageNetHandler(model_config.dict()):
            model = ImageNetHandler(model_config.dict())

        self.models[model_config.model_name] = model
        populate_tag_list(model.classes)


    def list_models(self) -> List[ModelHandler]:
        return list(self.models.values())
