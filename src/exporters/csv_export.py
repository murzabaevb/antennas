import csv

class CSVExport:
    def export(self, data, filename):
        """Export antenna data to a CSV file.

        Parameters
        ----------
        data : dict
            Antenna data from the `specs` property.
        filename : str
            Name of the output file.
        """
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            for key, value in data.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        writer.writerow([f"{key}.{subkey}", subvalue])
                else:
                    writer.writerow([key, value])
