import yaml

class YAMLExport:
    def export(self, data, filename):
        """Export the data to a YAML file."""
        with open(filename, 'w') as file:
            yaml.dump(data, file, default_flow_style=False)
