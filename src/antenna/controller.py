import importlib
import os
from antenna.base import BaseAntenna


class Antenna:
    """Controller for any antenna model."""

    def __init__(self, model_name):
        self._load_models()
        if model_name not in self._model_registry:
            raise ValueError(f"Unknown model '{model_name}'. Available: {list(self._model_registry.keys())}")
        self.model = self._model_registry[model_name]()

    def _load_models(self):
        """Dynamically load models from antenna_models/"""
        self._model_registry = {}
        for file in os.listdir('antenna_models'):
            if file.endswith('.py'):
                module_name = file[:-3]
                module = importlib.import_module(f'antenna_models.{module_name}')
                for cls in dir(module):
                    obj = getattr(module, cls)
                    if isinstance(obj, type) and issubclass(obj, BaseAntenna) and obj is not BaseAntenna:
                        self._model_registry[obj.__name__] = obj
    """
    def export(self, exporter, filename='export.csv'):
        data = self.model.specs()
        exporter.export(data, filename)
    """