import json

class JSONExport:
    def export(self, data, filename):
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
