from antenna.controller import Antenna
from exporters.csv_export import CSVExport
from exporters.json_export import JSONExport

# Create an ITU-F.1336 Sectoral antenna
ant2 = Antenna('ITUF1336s')

# Set antenna's parameters
ant2.model.set_params(
    oper_freq_mhz=500,
    max_gain_dbi=7.0,
    beamwidth_az_deg=30.0,
    beamwidth_el_deg=10.8,
    pattern_type='average',
    performance_type='improved',
    tilt_type='none',
    tilt_angle_deg=8,
    #k=0.9,
)

# test gain calculation
#print(ant2.model.gain(azimuth=0, elevation=13))

# test pattern diagrams


ant2.model.show_patterns()
#print(ant2.model.specs['h_pattern_datapoint']['loss'])
#print(f'\n')
#print(ant2.model.specs['v_pattern_datapoint']['loss'])
"""
# Export to CSV
csv_exporter = CSVExport()
ant.export(csv_exporter, filename='f1336_data.csv')
"""
# Export to JSON
#json_exporter = JSONExport()
#ant2.export(json_exporter, filename='f1336_data.json')
