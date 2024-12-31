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
        # Resolve the path to antenna_models relative to this file
        base_dir = os.path.dirname(__file__)  # Directory of controller.py
        models_dir = os.path.join(base_dir, 'antenna_models')

        if not os.path.exists(models_dir):
            raise FileNotFoundError(f"Directory not found: {models_dir}")

        for file in os.listdir(models_dir):
            if file.endswith('.py') and not file.startswith('__'):  # Ignore __init__.py
                module_name = file[:-3]
                module_path = f'antenna_models.{module_name}'
                module = importlib.import_module(module_path)
                for cls in dir(module):
                    obj = getattr(module, cls)
                    if isinstance(obj, type) and issubclass(obj, BaseAntenna) and obj is not BaseAntenna:
                        self._model_registry[obj.__name__] = obj


    def export(self, exporter, filename='export.csv'):
        """Export the current antenna model's specs using the given exporter.

        Parameters
        ----------
        exporter: An instance of an export class
            E.g., CSVExport, JSONExport, YAMLExport.
        filename: str
            The name of the output file.
        """
        self.model.export(exporter, filename)
