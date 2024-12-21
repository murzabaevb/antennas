from antenna.controller import Antenna
from exporters.csv_export import CSVExport
from exporters.json_export import JSONExport

# Create an ITU-F.1336 Sectoral antenna
ant = Antenna('ITUF1336s')

# Set antenna's parameters
ant.model.set_params(
    oper_freq_mhz=500,
    max_gain_dbi=17.0,
    beamwidth_az_deg=65.0,
    pattern_type='peak',
    performance_type='typical',
    tilt_type='mechanical',
    tilt_angle_deg=12,
)

#print(ant.model.params)

# test output
print(ant.model.gain(0, 0))
print(ant.model.gain(0, 90))
print(ant.model.gain(180, 270))
print(ant.model.gain(180, 0))

ant.model.show_patterns()
"""
# Export to CSV
csv_exporter = CSVExport()
ant.export(csv_exporter, filename='f1336_data.csv')

# Export to JSON
json_exporter = JSONExport()
ant.export(json_exporter, filename='f1336_data.json')
"""