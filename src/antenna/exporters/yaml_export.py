import yaml

class YAMLExport:
    def export(self, data, filename):
        """Export antenna data to a YAML file.

        Parameters
        ----------
        data : dict
            Antenna data from the `specs` property.
        filename : str
            Name of the output file.
        """
        with open(filename, 'w') as file:
            yaml.dump(data, file, default_flow_style=False)
