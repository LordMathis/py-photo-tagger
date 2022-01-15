from typing import List

import yaml as yaml
from pydantic import BaseModel


class ModelConfig(BaseModel):
    model_name: str

    module_path: str
    module_name: str

    class Config:
        extra = "allow"


class Config(BaseModel):
    models: List[ModelConfig]


def init_config(config_path: str) -> Config:
    with open(config_path, "r") as stream:
        return Config(**yaml.safe_load(stream))
