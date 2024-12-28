from antenna.controller import Antenna
from exporters import MSIExport
from exporters.msi_export import MSIExport
from exporters.csv_export import CSVExport
from exporters.json_export import JSONExport
from exporters.yaml_export import YAMLExport

# Create an Antenna instance
antenna = Antenna('ITUF699')

# Set parameters
antenna.model.set_params(
    oper_freq_mhz=23000,
    max_gain_dbi=45,
    diameter_m=6,
    # beamwidth_deg=1,
)

# Check set parameters
print(antenna.model.params)

# Calc. ant. gain
print(f'gain={antenna.model.gain(off_axis_angle=3):,.1f} dBi')

# Display patterns
antenna.model.show_patterns()

# Export to MSI file
exporter = MSIExport()
antenna.export(exporter, 'antenna_specs.msi')

# Set parameters
# antenna.model.set_params(
#     oper_freq_mhz=3500,
#     max_gain_dbi=17.0,
#     beamwidth_az_deg=65.0,
#     #beamwidth_el_deg=10.8,
#     pattern_type='average',
#     performance_type='improved',
#     tilt_type='mechanical',
#     tilt_angle_deg=60,
#     #k=0.9,
# )

# test gain calculation
# print(antenna.model.gain(azimuth=0, elevation=60))

# test CSV export function
# exporter = MSIExport()
# antenna.export(exporter, 'antenna_specs.msi')

# test diagram display
# antenna.model.show_patterns()

# test JSON export function
#exporter = JSONExport()
#antenna.export(exporter, 'antenna_specs.json')

# test YAML export function
#exporter = YAMLExport()
#antenna.export(exporter, 'antenna_specs.yaml')

# test MSI export function
#exporter = MSIExport()
#antenna.export(exporter, 'antenna_specs.msi')

# Create a log-gain antenna
#lg_ant = Antenna('ITUF1336lg')

# Set parameters
#lg_ant.model.set_params(
#    oper_freq_mhz=1000,
#    max_gain_dbi=10,
#)

# Test gain calc. function
#print(lg_ant.model.gain(off_axis_angle=31))

# Test diagram display function
#lg_ant.model.show_patterns()

# Test MSI export function
# exporter = MSIExport()
#lg_ant.export(exporter, 'antenna_specs.msi')