import json

class JSONExport:
    def export(self, data, filename):
        """Export antenna data to a JSON file.

        Parameters
        ----------
        data : dict
            Antenna data from the `specs` property.
        filename : str
            Name of the output file.
        """
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
